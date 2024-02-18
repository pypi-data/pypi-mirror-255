import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from os.path import join
from mdsdata.bunch import Bunch



DESCR = """
MDS-dataset 'MDS-4: Chemical Elements'
--------------------------------------

**Dataset Characteristics:**

    :Number of Instances: 38 (22 metals and 16 non-metals)
    :Number of Attributes: 4 numeric, predictive attributes and the class
    :Attribute Information:
        - atomic radius [pm]
        - electron affinity [kJ/mol]
        - ionization energy [kJ/mol]
        - electronegativity [-]
        - class:
                - non-metalliv (target value = 0)
                - metallic (target value = 1)

    :Summary Statistics:

    :Missing Attribute Values: None

    :Class Distribution: 22 and 16 examples for 2 classes.

    :Creator: The data file was extracted from the publication:
        J. J. V. Ferreira, M. T. S. Pinheiro, W. R. S. dos Santos, and
        R. da Silva Mai: "Graphical representation of chemical periodicity 
        of main elements through boxplot", Educación Química (2016) 27, 
        209---216, http://dx.doi.org/10.1016/j.eq.2016.04.007

    :Donor:

    :date May, 2023 

    This dataset contains four periodic properties: atomic radius, electron 
    affinity, ionization energy and the electronegativity. These properties 
    were collected for a total of 38 chemical elements (22 metals and 16 
    non-metals), originally taken from a number of different publicly 
    available sources.
"""








class MDS4:
    """MDS-dataset 'MDS-4: Chemical Elements'.
    
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
    p = join(os.path.dirname(os.path.abspath(__file__)), 'element_properties.csv')  


    def __init__(self) -> None:
        pass

    @staticmethod
    def load_data(*, return_X_y=False, as_frame=False):
        """Read and return data of the MDS-dataset 'MDS-4: Chemical Elements'.

        Chosen periodic properties of a number of metallic and non-metallic 
        elements.

        =================   ==============
        Classes                          2
        Samples per class        22 metals
                             16 non-metals
        Records total                   38
        Dimensionality                   4
        Features                      real
        =================   ==============

        More details can be found in the MDS book and at https://MDS-book.org

        The data file was extracted from the publication:
        J. J. V. Ferreira, M. T. S. Pinheiro, W. R. S. dos Santos, and 
        R. da Silva Mai: "Graphical representation of chemical periodicity of
        main elements through boxplot", Educación Química (2016) 27, 209---216
        http://dx.doi.org/10.1016/j.eq.2016.04.007

        
        Parameters
        ----------
        return_X_y : bool, default=False
            If True, returns ``(feature_matrix, target)`` instead of a 
            dictionary-like `Bunch` object (where items can be accessed
            using "."): 
            ``{feature_matrix, target, feature_names, taget_names, DESCR}``.

        as_frame : bool, default=False
            If True, the feature matrix is a pandas DataFrames, and the target
            is a pandas DataFrame or Series depending on the number of target 
            columns.


        Returns
        -------
        data : Either the feature matrix and target vector (the set of (X, y)) 
                or a "Bunch" (i.e., a dictionary where items can be accessed 
                using a dot) with the following attributes:

            feature_matrix : {ndarray, dataframe} of shape (38, 4)
                The feature matrix. If `as_frame=True`, `data` will be returned
                as a pandas DataFrame.
            data : this is the same as `feature_matrix`. It is kept for 
                compatibility with scikit-learn.
            target: {ndarray, Series} of shape (38,)
                The classification target. If `as_frame=True`, `target` will be
                a pandas Series.
            feature_names: list
                The names of the features (columns of the feature_matrix).
            target_names: list
                The names of target classes.
            frame: DataFrame of shape (38, 4)
                Only present when `as_frame=True`. DataFrame with `feature_matrix` and
                `target`.

            DESCR: str
                The full description of the dataset.
        """

        feature_names = np.array(['atomic_radius', 'electron_affinity', 'ionization energy', 'electronegativity'])
        label_names = ['metallic', 'non-metallic']

        df = pd.read_csv(MDS4.p)
        X = np.array(df[feature_names])
        y = np.array(df[['metallic']], dtype=int).flatten()

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




def load_elements():
    """Returns features (the element properties) and targets (class labels metallic or non-metallic)
    
    The label is 0 (="metallic") or 1 (='non-metallic')
    See `MDS4.load_data` for more information

    :returns: atomic_radius, electron_affinity, ionization_energy, electronegativity, label
    """
    data = MDS4.load_data()
    X = data.feature_matrix
    label = data.target
    features_names = data.feature_names
    
    atomic_radius = X[:, features_names == 'atomic_radius'].ravel()
    electron_affinity = X[:, features_names == 'electron_affinity'].ravel()
    ionization_energy = X[:, features_names == 'ionization_energy'].ravel()
    electronegativity = X[:, features_names == 'electronegativity'].ravel()

    return atomic_radius, electron_affinity, ionization_energy, electronegativity, label



def main():


    data = MDS4.load_data()
    X = data.feature_matrix
    y = data.target
    features_names = data.feature_names
    
    atomic_radius = X[:, features_names == 'atomic_radius'].ravel()
    electron_affinity = X[:, features_names == 'electron_affinity'].ravel()
    ionization_energy = X[:, features_names == 'ionization_energy'].ravel()
    electronegativity = X[:, features_names == 'electronegativity'].ravel()

    print(X)
    print(electron_affinity)
    return 

    data = MDS4.load_data()
    X = data.feature_matrix
    y = data.target
    features_names = data.feature_names


    atomic_radius = X[:, features_names == 'atomic_radius']
    electron_affinity = X[:, features_names == 'electron_affinity']
    print(atomic_radius)

    
    fig, ax = plt.subplots(figsize=(3.8, 2.5))
    mask = y == 1
    ax.plot(atomic_radius[mask], electron_affinity[mask], c='C0', lw=0, marker='o',  mec='C0', mfc='none', label='metallic')
    ax.plot(atomic_radius[~mask], electron_affinity[~mask], c='C1', lw=0, marker='o', mec='C1', mfc='none', label='non-meallic')
    ax.set(xlabel='atomic radius [pm]', ylabel='electron affinity [kJ/mol]')
    ax.legend()

    plt.tight_layout()
    #plt.show()
    plt.savefig('chemelem.png', pad_inches=0.1, bbox_inches='tight')


if __name__ == '__main__':
    main()