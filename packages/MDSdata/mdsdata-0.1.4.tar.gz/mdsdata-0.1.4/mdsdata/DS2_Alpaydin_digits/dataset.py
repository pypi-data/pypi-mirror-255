import gzip
import numpy as np
import os
from os.path import join
import pandas as pd
from mdsdata.bunch import Bunch




DESCR = """
MDS-Dataset 'DS-2 (light) -- 'Alpaydin' handwritten digits'
----------------------------------

**Dataset Characteristics:**

    :Number of Instances: 3823 (training) and 1797 (testing)
    :Number of Attributes: 8*8=64 numeric attributes and the class
    :Attribute Information: 
        8x8 image of integer pixels in the range 0..16.
        - target: integer value of digit (10 classes)

    :Class Distribution: for each of the 10 classes:
        Class:	No of examples in training set
        0:  376
        1:  389
        2:  380
        3:  389
        4:  387
        5:  376
        6:  377
        7:  387
        8:  380
        9:  382

        Class: No of examples in testing set
        0:  178
        1:  182
        2:  177
        3:  183
        4:  181
        5:  182
        6:  181
        7:  179
        8:  174
        9:  180

    :Creator: Datasets obtained from E. Alpaydin  (alpaydin@boun.edu.tr) and C. Kaynak 
    doi: 10.24432/C50P49,
    (https://archive.ics.uci.edu/dataset/80/optical+recognition+of+handwritten+digits), 
    original data: NIST

    :date June, 2023 

    The labels are the integer numbers of the digits. The original NIST data has
    been preproceed as detailed in the data repository (doi: 10.24432/C50P49)
"""

class DS2_light:
    """MDS-Dataset 'DS-2 light -- Alpaydin handwritten images'.
    
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
    p1 = join(os.path.dirname(os.path.abspath(__file__)), 'optical+recognition+of+handwritten+digits/optdigits.tra')
    p2 = join(os.path.dirname(os.path.abspath(__file__)), 'optical+recognition+of+handwritten+digits/optdigits.tes')
    
    def __init__(self) -> None:
        pass 

    @staticmethod
    def load_data(*, return_X_y=False, as_frame=False, verbose=False):
        """Read and return data of the MDS-Dataset 'DS-2 light -- Alpaydin handwritten images'
        
        The dataset consists of images of handwritten digits and the 
        corresponding integer numbers. All data was copied from
        https://archive.ics.uci.edu/dataset/80/optical+recognition+of+handwritten+digits.
        (https://doi.org/10.24432/C50P49)
        
        There are 3823+1797 training and testing images of 8x8 pixels in size. The target value
        range was scaled to 0..255 (the original range was 0..16). The training and testing
        dataset was appended, i.e. the first 3823 images are the training images.

        =================   ==============
        Records total                5620 
        Dimensionality                 64
        Features            integer, 0-255
        Targets             float, 0-9
        =================   ==============

        Parameters
        ----------
        return_X_y : bool, default=False
            If True, returns ``(data, target)`` instead of a 
            dictionary-like Bunch
            ``{data, target, target_names, DESCR, feature_names}``. 

        as_frame: bool, default=False
            If True, the feature matrix is a pandas DataFrames, and the target
            is a pandas DataFrame or Series depending on the number of target 
            columns.

        verbose: bool, default=False
            Enable additional output and information during reading the data.
        """

        images_train = pd.read_csv(DS2_light.p1, header=None)
        images_test = pd.read_csv(DS2_light.p2, header=None)

        images = pd.concat([images_train, images_test], axis=0, join='outer')
        images = np.array(images, dtype=int)
        targets = images[:,-1]
        images = images[:, :-1]

        print(images)
        print(targets)
        #return
        if verbose:
            print(images_train.shape)
            print(images_test.shape)
            print(images.shape)

        
        images = np.array(images, dtype=float) / 16 * 255
        images = images.reshape((images.shape[0], 8, 8))

        feature_names = ['array']
        label_names = ['digit']
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


def load_Alpaydin_digits():
    images, labels = DS2_light().load_data(return_X_y=True)
    return images, labels