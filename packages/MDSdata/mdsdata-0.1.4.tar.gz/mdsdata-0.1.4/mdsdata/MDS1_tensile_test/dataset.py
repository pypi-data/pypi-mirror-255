import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from os.path import join
from mdsdata.bunch import Bunch


DESCR = """
MDS-dataset MDS-1: Tensile Test with Parameter Uncertainties
----------------------------------------------------------------
        
**Dataset Characteristics:**

    :Number of Instances: 378 (.., .., .., .. for each of four classes)
    :Number of Attributes: 2 numeric, predictive attributes and the class
    :Attribute Information:
        - Young's modulus in GPa
        - indentation hardness in GPA
        - class:
                - 

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


class MDS1:
    """MDS-dataset 'Tensile Test with Parameter Uncertainties'.
    
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
    p1 = join(os.path.dirname(os.path.abspath(__file__)), 'strain.csv')  
    p2 = join(os.path.dirname(os.path.abspath(__file__)), 'stress.csv')

    def __init__(self) -> None:
        pass

    @staticmethod
    def load_data(*, temperature=0, return_X_y=False, as_frame=False, 
                  verbose=False):
        """Read and return data of the MDS-Dataset 'MDS-1 -- Tensile-Test'
        
        The dataset consists of pairs of stress-strain data obtained from
        a linear elastic material model with non-linear hardening and 
        temperature dependency. For each of the 3 temperature (0°C, 400°C, 
        600°C) the strain is the feature and the stress is the target. 
        Each of these 3 "sub-datasets" consists of altogether 350 data 
        records.

        =================   ==============
        Records total        for each temp.:  350
        Dimensionality                   1
        Features                      real
        Targets                       real
        =================   ==============

        Parameters
        ----------
        temperature: integer, default=0
            Possible values: 0, 400, 600 denote the temperature in
            degreees Celsiu.

        return_X_y: bool, default=False
            If True, returns ``(data, target)`` instead of a 
            dictionary-like Bunch
            ``{data, target, taget_names, DESCR, feature_names}``. 

        as_frame: bool, default=False
            If True, the feature matrix is a pandas DataFrames, and the target
            is a pandas DataFrame or Series depending on the number of target 
            columns.

        verbose: bool, default=False
            Enabl additional output and information during reading the data.
        """ 

        assert temperature in [0, 400, 600], \
            "temperature can only be 0, 400, or 600"

        df_strain = pd.read_csv(MDS1.p1)
        df_stress = pd.read_csv(MDS1.p2)

        columns = df_strain.columns  # first column label is empty (=index)
        if temperature == 0:
            strain = np.array(df_strain[columns[1]])
            stress = np.array(df_stress[columns[1]])
        elif temperature == 400:
            strain = np.array(df_strain[columns[2]])
            stress = np.array(df_stress[columns[2]])
        else:
            strain = np.array(df_strain[columns[3]])
            stress = np.array(df_stress[columns[3]])
        
        combined_frame = []
        feature_names = ['strain']
        target_names = ['stress']

        if as_frame:
            X = pd.DataFrame(data=strain, columns=feature_names)
            y = pd.DataFrame(data=stress, columns=target_names)
            combined_frame = pd.concat([X, y], axis=1)

        if return_X_y:
            return strain, stress

        return Bunch(
            feature_matrix=strain,
            data=strain,
            target=stress,
            feature_names=feature_names, 
            target_names=target_names, 
            frame = combined_frame,
            DESCR=DESCR,
        )


def load_tensile_test(temperature=600):
    strain, stress = MDS1.load_data(temperature=temperature, 
                                    return_X_y=True)
    return strain, stress