import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from os.path import join
from mdsdata.bunch import Bunch


DESCR = """
MDS-dataset MDS-5: Nanoindentation CuCr composites
--------------------------------------------------
        
**Dataset Characteristics:**

    :Number of Instances: 378 (.., .., .., .. for each of four classes)
    :Number of Attributes: 2 numeric, predictive attributes and the class
    :Attribute Information:
        - Young's modulus in GPa
        - indentation hardness in GPA
        - class:
                - '0% Cr'
                - '25% Cr'
                - '60% Cr'
                - '100% Cr'

    :Summary Statistics:

    :Missing Attribute Values: None

    :Class Distribution: ... for each of 4 classes.

    :Creator: Chen Zhang, Clémence Bos, Stefan Sandfeld, Ruth Schwaiger

    :Donor:

    :date July, 2023 

    
    Nanoindentation of four different Cu/Cr composites. The dataset has two 
    features, the Young's modulus E and the hardness H, both of which are 
    given in GPa.

    The data file is part of the supplementary material of the publication:
    Chen Zhang, Clémence Bos, Stefan Sandfeld, Ruth Schwaiger: "Unsupervised 
    Learning of Nanoindentation Data to Infer Microstructural Details of 
    Complex Materials, https://arxiv.org/abs/2309.06613 which can also be 
    found at https://doi.org/10.5281/zenodo.8336072

    Please reference these publications if you are using the dataset or methods
    for your own research.

    By default, outliers are removed, and the total number of data records is 
    the above given number. If the outlier (e.g., for the purpose of an 
    exercise) are required, then the above given total number of records and 
    samples per class will be different ones.             
"""


class MDS5:
    """MDS-dataset 'MDS-5: Nanoindentation'.
    
    The interface of the `load_data` method has been designed to conform closely
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
    p0 = join(os.path.dirname(os.path.abspath(__file__)), 'data/Cr0_full.csv')  
    p25 = join(os.path.dirname(os.path.abspath(__file__)), 'data/Cr25_full.csv')
    p60 = join(os.path.dirname(os.path.abspath(__file__)), 'data/Cr60_full.csv')
    p100 = join(os.path.dirname(os.path.abspath(__file__)), 'data/Cr100_full.csv') 

    p0red = join(os.path.dirname(os.path.abspath(__file__)), 'data/Cr0_reduced.csv')  
    p25red = join(os.path.dirname(os.path.abspath(__file__)), 'data/Cr25_reduced.csv')
    p60red = join(os.path.dirname(os.path.abspath(__file__)), 'data/Cr60_reduced.csv')
    p100red = join(os.path.dirname(os.path.abspath(__file__)), 'data/Cr100_reduced.csv') 

    def __init__(self) -> None:
        pass

    @staticmethod
    def load_data(*, outlier=False, return_X_y=False, as_frame=False):
        """Read and return data of the MDS-dataset 'MDS-5: Nanoindentation'.
        
        Nanoindentation of four different Cu/Cr composites. The dataset has two
        features, the Young's modulus E and the hardness H, both of which are 
        given in GPa.

        =================   ==============
        Classes                          4
        Samples per class      ??/??/??/??
        Records total                  938
        Dimensionality                   2
        Features            real, positive
        =================   ==============

        More details can be found in the MDS book and at https://MDS-book.org

        The data file is part of the supplementary material of the publication:
        Chen Zhang, Clémence Bos, Stefan Sandfeld, Ruth Schwaiger: "Unsupervised 
        Learning of Nanoindentation Data to Infer Microstructural Details of 
        Complex Materials, https://arxiv.org/abs/2309.06613 which can also be 
        found at https://doi.org/10.5281/zenodo.8336072

        Please reference these publications if you are using the dataset or methods
        for your own research.
        
        Parameters
        ----------
        return_X_y: bool, default=False
            If True, returns ``(data, target)`` instead of a 
            dictionary-like Bunch
            ``{data, target, taget_names, DESCR, feature_names}``. 

        as_frame : bool, default=False
            If True, the feature matrix is a pandas DataFrames, and the target
            is a pandas DataFrame or Series depending on the number of target 
            columns.

        outlier: bool, default=False
            In the default case, outliers are removed, and the total number of
            data records is the above given number. If the outlier (e.g., 
            for the purpose of an exercise) are required, then the above
            given total number of records and samples per class are different.


        Returns
        -------
        data : Either the feature matrix and target vector (the set of (X, y)) 
                or a "Bunch" (i.e., a dictionary where items can be accessed 
                using a dot) with the following attributes:

            feature_matrix : {ndarray, dataframe} of shape (???, 2)
                The feature matrix. If `as_frame=True`, `data` will be returned
                as a pandas DataFrame.
            data : this is the same as `feature_matrix`. It is kept for 
                compatibility with scikit-learn.
            target: {ndarray, Series} of shape (150,)
                The classification target. If `as_frame=True`, `target` will be
                a pandas Series.
            feature_names: list
                The names of the features (columns of the feature_matrix).
            target_names: list
                The names of target classes.
            frame: DataFrame of shape (???, 3)
                Only present when `as_frame=True`. DataFrame with `data` and
                `target`.

            DESCR: str
                The full description of the dataset.
        """

        _feature_names = ["Young's modulus", "hardness"]
        label_names = ['0% Cr', '25% Cr', '60% Cr', '100% Cr']
        modulus, hardness, class_id = [], [], []

        if outlier:
            paths = [MDS5.p0, MDS5.p25, MDS5.p60, MDS5.p100]
        else:
            paths = [MDS5.p0red, MDS5.p25red, MDS5.p60red, MDS5.p100red]

        for i, p in enumerate(paths):
            df = pd.read_csv(p)
            modulus += df['E'].tolist()
            hardness += df['H'].tolist()
            class_id += df['E'].size * [i]
        
        X = np.stack((modulus, hardness), axis=0).T
        y = np.array(class_id, dtype=int)
        combined_frame = []

        if as_frame:
            X = pd.DataFrame(data=X, columns=_feature_names)
            y = pd.DataFrame(data=y, columns=['target'])
            combined_frame = pd.concat([X, y], axis=1)

        if return_X_y:
            return X, y

        return Bunch(
            feature_matrix=X,
            data=X,
            target=y,
            feature_names=_feature_names, 
            target_names=label_names, 
            frame = combined_frame,
            DESCR=DESCR,
        )


def load_indentation():
    """Returns features (youngs modulus and hardness) and targets 
    (class: 0-3, i.e. '0% Cr', '25% Cr', '60% Cr', '100% Cr')
    
    Outlier are already removed.
    See `MDS5.load_data` for more information
    """
    CuCr = MDS5.load_data(outlier=True)
    X = CuCr.feature_matrix
    y = CuCr.target 
    modulus = X[:, 0]
    hardness = X[:, 1]
    material = y
    
    return modulus, hardness, material