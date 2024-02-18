import gzip
import numpy as np
import os
from os.path import join
import pandas as pd
import matplotlib.pyplot as plt

from mdsdata.bunch import Bunch


DESCR = """
MDS-Dataset 'DS-2 -- MNIST handwritten digits'
----------------------------------

**Dataset Characteristics:**

    :Number of Instances: 60k + 10k (train + test)
    :Number of Attributes: 28*28=784 numeric attributes and the class
    :Attribute Information: 
        64x64 image of integer pixels in the range 0..255.
        - target: integer value of digit

    :Class Distribution: for each of the 10 classes:
        train (0-9): 5923, 6742, 5958, 6131, 5842, 5421, 5918, 6265, 5851, 5949
        test (0-9): 980, 1135, 1032, 1010,  982,  892,  958, 1028,  974, 1009

    :Creator: Datasets obtained from Yann LeCun, original data: NIST

    :date May, 2023 

    The labels are the integer numbers of the digits.


    Raw data was obtained the web page of Yann LeCun by:

    mkdir -f ./data
    wget http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz
    wget http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz
    wget http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz
    wget http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz

    mv train-images-idx3-ubyte.gz train-labels-idx1-ubyte.gz t10k-images-idx3-ubyte.gz t10k-labels-idx1-ubyte.gz data
"""

class DS2:
    """MDS-Dataset 'DS-2 -- MNIST handwritten digits'.
    
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
    p_train_img = join(os.path.dirname(os.path.abspath(__file__)), 'data/train-images-idx3-ubyte.gz')
    p_train_lbl = join(os.path.dirname(os.path.abspath(__file__)), 'data/train-labels-idx1-ubyte.gz')
    p_test_img = join(os.path.dirname(os.path.abspath(__file__)), 'data/t10k-images-idx3-ubyte.gz')
    p_test_lbl = join(os.path.dirname(os.path.abspath(__file__)), 'data/t10k-labels-idx1-ubyte.gz')

    
    @staticmethod
    def __read_images(filename):
        # adapted from https://stackoverflow.com/a/62781370/12343828

        with gzip.open(filename, 'r') as f:
            # first 4 bytes is a magic number
            magic_number = int.from_bytes(f.read(4), 'big')

            # second 4 bytes is the number of images
            image_count = int.from_bytes(f.read(4), 'big')

            # third 4 bytes is the row count
            row_count = int.from_bytes(f.read(4), 'big')

            # fourth 4 bytes is the column count
            column_count = int.from_bytes(f.read(4), 'big')

            # rest is the image pixel data, each pixel is stored as an unsigned byte
            # pixel values are 0 to 255
            image_data = f.read()
            images = np.frombuffer(image_data, dtype=np.uint8)\
                .reshape((image_count, row_count, column_count))
            return images

    @staticmethod
    def __read_labels(filename):
        # adapted from https://stackoverflow.com/a/62781370/12343828

        with gzip.open(filename, 'r') as f:
            # first 4 bytes is a magic number
            magic_number = int.from_bytes(f.read(4), 'big')

            # second 4 bytes is the number of labels
            label_count = int.from_bytes(f.read(4), 'big')

            # rest is the label data, each label is stored as unsigned byte
            # label values are 0 to 9
            label_data = f.read()
            labels = np.frombuffer(label_data, dtype=np.uint8)
            return labels

    @staticmethod
    def load_data(*, return_X_y=False, as_frame=False, verbose=False, train=True):
        """Read and return data of the MDS-Dataset 'DS-2 -- MNIST handwritten digits'
        
        The dataset consists of images of handwritten digits and the 
        corresponding integer numbers. All data was copied from
        http://yann.lecun.com/exdb/mnist/.
        
        The images are stored in a ZIP archive and will be extracted 
        as numpy arrays. There are 60k + 10k images of 28x28 pixels in size.

        =================   ==============
        Records total       train:  60,000
                            test:   10,000
        Dimensionality      28 * 28 = 784      
        Features            unsigned integer, (0-255)
        Targets             digit: integer (0-9)
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

        train: bool, default=True
            If True, creates dataset from train-images-idx3-ubyte (which was 
            originally the training dataset), otherwise from 
            t10k-images-idx3-ubyte (which was originally the test dataset).

        """
        if train:
            images = DS2.__read_images(DS2.p_train_img)
            targets = DS2.__read_labels(DS2.p_train_lbl)
        else:
            images = DS2.__read_images(DS2.p_test_img)
            targets = DS2.__read_labels(DS2.p_test_lbl)

        feature_names = ['array']
        label_names = ['digits']
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
    

def load_MNIST_digits(train=True):
    images, labels = DS2().load_data(return_X_y=True, train=train)
    return images, labels