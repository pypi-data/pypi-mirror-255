import os
import cv2
from tqdm.auto import tqdm
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from sklearn.decomposition import PCA
import plotly.express as px
import pandas as pd
import seaborn as sns
import scipy.stats
from PIL import Image
import shutil
import yaml
from ipywidgets import HTML, VBox
from plotly import graph_objects as go
import plotly.io as pio

pio.renderers.default = "notebook"


def load_img(path, size):
    """
    Simple util for image loading.
    Parameters:
    - path: path to image
    - size: target image size
    """
    im = Image.open(path)
    im = im.resize(size)
    return im


class Owl:
    """
    This class represents image dataset from directory (we call it gallery). Currently it supports methods 
    for plotting image data and tools like apply or undersampling.  
    """
    def __init__(self, gallery):
        """
        Initializes dataset from directory
        Parameters:
        - gallery: path to directory with images
        """
        self.gallery = gallery
        self.filenames = os.listdir(self.gallery)
        self.data = np.array([load_img(f"{self.gallery}/{image_file}", (420,420)) for image_file in tqdm(self.filenames, desc="Loading")])
        self.cached_features_dataframe = None
        

    def apply(self, func, inplace=False):
        """
        Applies function to whole dataset (self.data)
        Parameters:
        - func: function to apply
        - inplace: should owl inplace current image with new ones. if
        false just returns processed data.
        """
        result = np.array(list(map(func, self.data)))
        if inplace == True:
            self.data = result
        else:
            return result
        

    def random_plot(self, n_images):
        """
        Plots N random images in subplots. Useful thing while exploring at your data.
        Parameters:
        - n_images: amout of images to plot
        """
        images = []
        for _ in range(n_images):
            idx = np.random.randint(len(self.data))
            images.append(self.data[idx])
            
        n_cols = int(np.ceil(np.sqrt(n_images)))
        n_rows = int(np.ceil(n_images / n_cols))
        
        fig, axes = plt.subplots(n_rows, n_cols)
        axes = axes.flatten()
        
        for i, (ax, image) in enumerate(zip(axes, images)):
            ax.imshow(image)
            ax.axis('off')
        
        for ax in axes[n_images:]:
            ax.axis('off')
        
        plt.tight_layout()
        plt.show()
        
        
    def _get_features(self):
        """
        Extracts features from images (self.data) with Resnet50 and PCA. After 
        processing returns pd.DataFrame with components x & y and filenames.
        Because feature extraction is long operation we are caching data 
        in self.cached_features_dataframe.
        """
        if self.cached_features_dataframe is not None:
            return self.cached_features_dataframe
        else:
            model = ResNet50(weights='imagenet', include_top=False)
            images = self.apply(preprocess_input)
            features = model.predict(images)
            features = features.reshape(len(features), np.prod(features.shape[1:]))
            
            pca = PCA(n_components=2)
            pca_features = pca.fit_transform(features)
            
            x = [i[0] for i in pca_features]
            y = [i[1] for i in pca_features]
            
            df = pd.DataFrame()
            df["x"] = x
            df["y"] = y
            df["filenames"] = self.filenames
            df["filenames"] = df["filenames"].apply(lambda x: f"{self.gallery}/{x}")
            self.cached_features_dataframe = df
            
            return df
        
    def distplot(self, kind="scatter"):
        """
        Creates 2d plot based on extracted features. You can use to show distribution
        of images on your dataset and analyze clusters.
        Parameters:
        - kind: how to plot. currently there're 3 type of plots supported:
            * scatter - plotly scatter and filename on hover
            * iscatter - interactive scatter that show image on hover inside jupyter noteboook.
            * joint - hex 2dim plot (sns.jointplot used)
        """
        df = self._get_features()
        if kind == "scatter":
            fig = px.scatter(df, x="x", y="y", title="Images Distribution", hover_data="filenames")
            fig.show("notebook")
        elif kind == "joint":
            sns.jointplot(x="x", y="y", kind="hex", data=df) 
            plt.show() 
        elif kind == "iscatter":
            fig = px.scatter(df, x="x", y="y", title="Images Distribution", hover_data="filenames")
            template="<img src='{filenames}'>"
            html = HTML("")

            def update(trace, points, state):
                ind = points.point_inds[0]
                row = df.loc[ind].to_dict()
                html.value = template.format(**row)

            fig = go.FigureWidget(data=fig.data, layout=fig.layout)
            fig.data[0].on_hover(update)

            return VBox([fig, html])
            
            
    def undersample(self, target_size):
        """
        Undersamples dataset with kde-method. Returns filepaths of undersampled set and plots main sample
        and undersampled set on top to view distribution.
        Parameters:
        - target_size: target size of subsample, must be lower than size of dataset.
        """
        assert target_size < len(self.data)
        df = self._get_features()
        data = np.array(list(zip(df["x"].values,df["y"].values)))
        kde = scipy.stats.gaussian_kde(data.T)
        p = 1 / kde.pdf(data.T)
        p /= np.sum(p)
        idx = np.random.choice(np.arange(len(data)), size=target_size, replace=False, p=p)
        sample = data[idx]
        
        plt.figure()
        plt.scatter(data[:, 0], data[:, 1], label='Data', s=10)
        plt.scatter(sample[:, 0], sample[:, 1], label='Sample', s=7)
        plt.legend()
        
        return df.filenames.values[idx]
    
    def copy_to(self, destination):
        """
        Copies all images from gallery to another gallery called destination.
        Parameters:
        - destination: directory, where you want to copy images. if folder not exists we'll
        create it.
        """
        if not os.path.exists(destination):
            os.makedirs(destination)
        for file in tqdm(self.filenames, desc="Copying"):
            shutil.copy(os.path.join(self.gallery, file), destination)
            
            
class DataChecker:
    """
    This class is used for checking dataset validity and markup scanning. It supports tools like
    checking annotations or plotting pretty charts to view samples per class in your labels.
    """
    def __init__(self, task, gallery, annotations, metadata, classlist=None):
        """
        Initializes DataChecker instance.
        Parameters:
        - task: CV task, could be classification or detection
        - gallery: path to directory with images
        - annotations: path to folder with annotations
        - metadata: metadata file, required for detection (data.yaml in ultralytics YOLO)
        - classlist: list with classnames in classification task
        """
        self.task = task
        self.gallery_path = gallery
        self.annotations_path = annotations
        self.metadata = metadata
        self.images = os.listdir(self.gallery_path)
        self.labels = os.listdir(self.annotations_path)
        self.classlist = classlist
        
        
    def _parse_detection_meta(self):
        """
        Parse self.metadata yaml file
        """
        with open(self.metadata, "r") as metafile:
            contents = yaml.safe_load(metafile)
        return contents
    
    def _parse_detection_annotation(self, filepath):
        """
        Parse annotation file in detection task. Returns list of floats (coordinates) 
        and ints (classes).
        """
        with open(filepath, "r") as f:
            contents = f.read().split()
            contents = list(map(float, contents))
            contents[0] = int(contents[0])
        return contents
      
    def _parse_classification_annotation(self, filepath):
        """
        Parse annotation file in classification task. Returns int (class id).
        """
        with open(filepath, "r") as f:
            contents = f.read().split()
            contents = int(contents[0])
        return contents
    
    def check(self):
        """
        Checks dataset validity based on self.task. Finally generates report 
        that shows validity of data. 
        """
        _warnings = 0
        length_check = (len(self.images) == len(self.labels))
        report = f"Check Report:\nSample Length Check: {length_check}\n"
        if length_check == False:
            _warnings += 1
            
        if self.task == "classification":
            for fn in tqdm(self.labels, desc="Check"):
                fn = os.path.join(self.annotations_path, fn)
                try:
                    label = self._parse_classification_annotation(fn)
                except:
                    report += f"File {fn}: can't read annotation\n"
                    _warnings += 1
                    continue
        elif self.task == "detection":
            metadata = self._parse_detection_meta()
            for fn in tqdm(self.labels, desc="Check"):
                fn = os.path.join(self.annotations_path, fn)
                label = self._parse_detection_annotation(fn)
                if len(label) % 5 != 0:
                    report += f"File {fn}: annotation items length shoud be divisible by 5\n"
                    _warnings += 1
                    continue
                else:
                    for i in range(len(label)%5+1):
                        cls = label[i*5]
                        if cls < 0 or cls > metadata["nc"]:
                            report += f"File {fn}: annotation class should be in range nc\n"
                            _warnings += 1
                            continue
        if _warnings > 0:
            report += f"Warnings found: {_warnings}. Please check report logs!"
        else:
            report += f"Everything is OK!"
            
        print(report)
        
    
    def class_counts(self):
        """
        Counts samples per each class and create interactive bar chart 
        with class names and samples per each class. For classification task 
        self.classlist should be provided.
        """
        if self.task == "classification":
            class_names = self.classlist
            samples_per_class = [0 for i in range(len(class_names))]
                    
            for fn in tqdm(self.labels, desc="Scanning"):
                fn = os.path.join(self.annotations_path, fn)
                label = self._parse_classification_annotation(fn)[0]
                samples_per_class[label] += 1
                
            df = pd.DataFrame({"names": class_names, "counts": samples_per_class})
            
            fig = px.bar(df, y='counts', x='names', text='counts')
            fig.update_traces(textposition='outside')
            fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
            fig.show()
        elif self.task == "detection":
            metadata = self._parse_detection_meta()
            class_names = metadata["names"]
            samples_per_class = [0 for i in range(len(class_names))]
                    
            for fn in tqdm(self.labels, desc="Scanning"):
                fn = os.path.join(self.annotations_path, fn)
                label = self._parse_detection_annotation(fn)[0]
                samples_per_class[label] += 1
                
            df = pd.DataFrame({"names": class_names, "counts": samples_per_class})
            
            fig = px.bar(df, y='counts', x='names', text='counts')
            fig.update_traces(textposition='outside')
            fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
            fig.show()
