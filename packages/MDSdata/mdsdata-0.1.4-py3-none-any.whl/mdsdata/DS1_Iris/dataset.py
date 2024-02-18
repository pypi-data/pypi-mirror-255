import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from os.path import join
from mdsdata.bunch import Bunch



DESCR = """
MDS-dataset 'DS-1: Iris Flower Dataset'
--------------------------------------

**Dataset Characteristics:**

    :Number of Instances: 150 (3 classes/flowers of 50 instances)
    :Number of Attributes: 4 numeric, predictive attributes and the class
    :Attribute Information:
        - sepal length in cm
        - sepal width in cm
        - petal length in cm
        - petal width in cm
        - class: class of iris plant (Iris Setosa, Iris Versicolor, Iris Virginica)
                

    :Summary Statistics:
	              Min  Max   Mean    SD   Class Correlation
    sepal length: 4.3  7.9   5.84  0.83    0.7826   
    sepal width: 2.0  4.4   3.05  0.43   -0.4194
    petal length: 1.0  6.9   3.76  1.76    0.9490  (high!)
    petal width: 0.1  2.5   1.20  0.76    0.9565  (high!)

    :Missing Attribute Values: None

    :Class Distribution: 33.3% for each of 3 classes.

    :Creator: R.A. Fisher

    :Donor: Michael Marshall (MARSHALL%PLU@io.arc.nasa.gov)

    :date May, 1988

    Obtained from the UC Irvine Machine Learning Repository
    DOI: 10.24432/C56C76
    This dataset is licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license.
    https://creativecommons.org/licenses/by/4.0/legalcode
    This allows for the sharing and adaptation of the datasets for any purpose, provided that the appropriate credit is given.


    Fisher's paper is a classic in the field
    and is referenced frequently to this day.  (See Duda & Hart, for
    example.)  The data set contains 3 classes of 50 instances each,
    where each class refers to a type of iris plant.  One class is
    linearly separable from the other 2; the latter are NOT linearly
    separable from each other.
"""








class DS1:
    """MDS-dataset 'DS-1: Iris Flower Dataset'.
    
    The interface of the `data` method has been designed to conform closely
    with the well-established interface of scikit-learn (see 
    https://scikit-learn.org/stable/datasets.html). The only difference is
    that the returned dictionary-like `Bunch` also contains `feature_matrix`,
    which is an alias for scikit-learn's `data` array/dataframe.
    """  
        
    # The absolute path is required when importing this package! Otherwise
    # a wrong relative path is resolved and reading a file from within this
    # script does not work properly. You can see this with
    # `print(os.path.dirname(os.path.abspath(__file__)))`
    p = join(os.path.dirname(os.path.abspath(__file__)), 'iris.csv')  


    def __init__(self) -> None:
        pass

    @staticmethod
    def load_data(*, return_X_y=False, as_frame=False):
        """Read and return data of the MDS-dataset 'MDS-4: Chemical Elements'.

        Classification of three different types if Iris plants based on four
        measurements of the size of the petals and sepals.

        =================   ==============
        Classes                          3
        Samples per class               50
        Records total                   150
        Dimensionality                   4
        Features                      real
        =================   ==============

        attributes: sepal length, sepal width, petal length, petal width in cm
        classes: Iris-setosa, Iris-versicolor, Iris-virginica

        More details can be found in the MDS book and at https://MDS-book.org

        Obtained from the UC Irvine Machine Learning Repository
        DOI: 10.24432/C56C76
        This dataset is licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license.
        https://creativecommons.org/licenses/by/4.0/legalcode
        This allows for the sharing and adaptation of the datasets for any purpose, provided that the appropriate credit is given.


        
        Parameters
        ----------
        return_X_y : bool, default=False
            If True, returns ``(feature_matrix, target)`` instead of a 
            dictionary-like `Bunch` object (where items can be accessed
            using "."): 
            ``{feature_matrix, target, feature_names, target_names, DESCR}``.

        as_frame : bool, default=False
            If True, the feature matrix is a pandas DataFrames, and the target
            is a pandas DataFrame or Series depending on the number of target 
            columns.


        Returns
        -------
        data : Either the feature matrix and target vector (the set of (X, y)) 
                or a "Bunch" (i.e., a dictionary where items can be accessed 
                using a dot) with the following attributes:

            feature_matrix : {ndarray, dataframe} of shape (150, 4)
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
            frame: DataFrame of shape (150, 4)
                Only present when `as_frame=True`. DataFrame with `feature_matrix` and
                `target`.

            DESCR: str
                The full description of the dataset.
        """

        feature_names = ['sepal length', 'sepal width', 'petal length', 'petal width']
        label_names = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']

        df = pd.read_csv(DS1.p, header=None)
        df.columns = feature_names + ['class label']
        X = np.array(df[feature_names])

        class_map = {s: i for i, s in enumerate(label_names)}
        df['target'] = np.array([class_map[key] for key in df['class label']])
        y = np.array(df[['target']], dtype=int).flatten()

        combined_frame = []

        if as_frame:
            X = pd.DataFrame(data=X, columns=feature_names)
            y = pd.DataFrame(data=y, columns=['target'])
            combined_frame = pd.concat([X, y], axis=1)

        if return_X_y:
            return X, y

        return Bunch(
            feature_matrix=X,
            data=X,
            target=y,
            feature_names=feature_names, 
            target_names=label_names, 
            frame = combined_frame,
            DESCR=DESCR,
        )




def load_iris():
    """Returns features (the element properties) and targets (class labels metallic or non-metallic)
        
    See `DS1.load_data` for more information
    """
    data = DS1.load_data(as_frame=True)
    X = data.feature_matrix
    species_id = np.array(data.target, dtype=int).ravel()
    sepal_length = np.array(data.frame['sepal length'])
    sepal_width = np.array(data.frame['sepal width'])
    petal_length = np.array(data.frame['petal length'])
    petal_width = np.array(data.frame['petal width'])
    return sepal_length, sepal_width, petal_length, petal_width, species_id



def main():

    data = DS1.load_data(as_frame=True)
    print(data.frame)
    X = data.feature_matrix
    y = data.target

    sepal_length, sepal_width, petal_length, petal_width, species_id = load_iris()
    print(species_id)

if __name__ == '__main__':
    main()