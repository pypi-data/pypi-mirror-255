import numpy as np
import os
from os.path import join
import pandas as pd

import matplotlib.pyplot as plt
from mdsdata.io import get_Ising_images_temperatures_and_labels
from mdsdata.bunch import Bunch


DESCR = """
MDS-Dataset 'MDS-2 -- Ising Model'
----------------------------------

**Dataset Characteristics:**

    :Number of Instances: 5000 (2507 and 2493 for the two classes)
    :Number of Attributes: 4096 numeric attributes and the class
    :Attribute Information: 
        64x64 image of integer pixels in the range 0..255.
        - target: temperature value
        - class:
                - 0: below Curie temperature
                - 1: above Curie temperature

    :Class Distribution: 2507 and 2493 for the two classes.

    :Creator: Sebastien Bompas, Stefan Sandfeld

    :date May, 2023 

    The labels (0 or 1) indicate if the temperature is below (0) or 
    above the Curie temperature (1).
"""


class MDS2:
    """MDS-Dataset 'MDS-2 -- Ising Model'.
    
    The interface of the `data` method has been designed to conform closely
    with the well-established interface of scikit-learn (see 
    https://scikit-learn.org/stable/datasets.html). The only difference is
    that the returned dictionary-like `Bunch` also contains `feature_matrix`,
    which is an alias for scikit-learn's `data` array/dataframe.

    See the documentation of `load_data` for further details.
    """  

    # The absolute path is required when importing this package! Otherwise
    # a wrong relative path is resolved and reading a file from within this
    # script does not work properly. You can see this with
    # `print(os.path.dirname(os.path.abspath(__file__)))`
    p = join(os.path.dirname(os.path.abspath(__file__)), 'images_64.zip')
    p2 = join(os.path.dirname(os.path.abspath(__file__)), 'labels_64.csv')
    
    def __init__(self) -> None:
        pass 

    @staticmethod
    def load_data(*, return_X_y=False, as_frame=False, verbose=False):
        """Read and return data of the MDS-Dataset 'MDS-2 -- Ising Model'
        
        The dataset consists of images of magnetic microstructures and the 
        corresponding temperature values obtained from simulations with
        the Cahn-Hilliard model. Each data record is obtained from an 
        individual simulation.
        
        The images are stored in a ZIP archive and will be extracted 
        of numpy arrays. There are 5000 images of 64x64 pixels in size.

        =================   ==============
        Records total                 5000
        Dimensionality                4096
        Features            integer, 0/255
        Targets             temperature: real (>0)
                            above_Tc: 0 or 1
        =================   ==============

        Parameters
        ----------
        return_X_y : bool, default=False
            If True, returns ``(data, target)`` instead of a 
            dictionary-like Bunch
            ``{data, target, taget_names, DESCR, feature_names}``. 

        as_frame: bool, default=False
            If True, the feature matrix is a pandas DataFrames, and the target
            is a pandas DataFrame or Series depending on the number of target 
            columns.

        verbose: bool, default=False
            Enable additional output and information during reading the data.
        """

        images, temperatures, labels = \
            get_Ising_images_temperatures_and_labels(
                zip_filename=MDS2.p, 
                csv_filename=MDS2.p2,
                verbose=verbose
            )
        
        images = np.array(images, dtype=int)
        temperatures = np.array(temperatures, dtype=float)
        targets = np.stack((temperatures, labels), axis=0).T
        feature_names = ['array']
        label_names = ['temperature', 'above_Tc']
        combined_frame = []

        if as_frame:
            X = pd.DataFrame(data=images, columns=feature_names)
            y = pd.DataFrame(data=targets, columns=label_names)
            combined_frame = pd.concat([X, y], axis=1)

        if return_X_y:
            return images, targets
        
        return Bunch(
            feature_matrix=images,
            data=images,
            target=targets,
            feature_names=feature_names, 
            target_names=label_names, 
            frame=combined_frame,
            DESCR=DESCR,
        )


def load_Ising():
    """Returns features (the images), labels (0/1 for below/above Tc) and temperature
    
    See `MDS2.load_data` for more information
    """
    images, targets = MDS2.load_data(return_X_y=True)
    temperatures = targets[:, 0]
    labels = np.array(targets[:, 1], dtype=int)

    return images, labels, temperatures