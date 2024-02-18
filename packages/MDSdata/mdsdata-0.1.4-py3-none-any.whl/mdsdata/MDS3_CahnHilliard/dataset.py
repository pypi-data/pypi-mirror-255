import numpy as np
from numpy import ndarray
import pandas as pd
from tqdm import tqdm
import os
import os.path
from os.path import join
import matplotlib.pyplot as plt

from mdsdata.io import get_CahnHilliard_images_and_energies
from mdsdata.bunch import Bunch


DESCR = """
MDS-Dataset 'MDS-3 -- Cahn-Hilliard'
------------------------------------
        
**Dataset Characteristics:**

    :Number of Instances: ??? (.., .., .., .. for each of four classes)
    :Number of Attributes: 4096 numeric, predictive attributes and the class
    :Attribute Information:
        - 
        - 
        - class:
                - 0:
                - 1:

    :Class Distribution: ... for each of the 2 classes.

    :Creator: Binh Duong Nguyen, Stefan Sandfeld

    :date May, 2023 
  

    The whole dataset consists of 18 simulations. For each,
    two files are required: a zip archiv that contains a number of
    images without any directory, and a csv file that contains three
    columns with the names (as first row):
    filenames,energy
    The filenames must correspond to the the names in the zip archive.           
"""


class MDS3:
    """MDS-Dataset 'MDS-3 -- Cahn-Hilliard'

    The interface of the `load_data` method has been designed to conform closely
    with the well-established interface of scikit-learn (see 
    https://scikit-learn.org/stable/datasets.html). The only difference is
    that the returned dictionary-like `Bunch` also contains `feature_matrix`,
    which is an alias for scikit-learn's `data` array/dataframe.

    See the documentation of `load_data` for further details.
    """

    pixels = (64, 64)

    # The absolute path is required when importing this package! Otherwise
    # a wrong relative path is resolved and reading a file from within this
    # script does not work properly. You can see this with
    # `print(os.path.dirname(os.path.abspath(__file__)))`
    p = join(os.path.dirname(os.path.abspath(__file__)), 'data')

    def __init__(self) -> None:
        pass

    @staticmethod
    def load_data(*, simulation_number=-1, return_X_y=False, as_frame=False, 
                  verbose=False):
        """Read and return data of the MDS-Dataset 'MDS-3 -- Cahn-Hilliard'
        
        The dataset consists of images of phase microstructures and the 
        corresponding energie values obtained from altogether 18 simulations 
        of the Cahn-Hilliard model. 
        
        The images are stored in a ZIP archive and will be extracted 'on the
        fly'. There are 17866 images of 64x64 pixels in size.
        
        The microstructures-energy pairs were shuffled, i.e., they do not occur
        in the same order as the evolution of the simulation. If this is 
        required, one can eailsy sort them according to decreasing energy.

        =================   ==============
        Records total                17866
        Dimensionality                4096
        Features            integer, 0-255
        Targets             real, positive
        =================   ==============

        Parameters
        ----------
        simulation_number: (0..17) if given (as int or list of ints), then only these 
            simulations will be read. Otherwise, all 18 simulations will be read
            and returned.

        return_X_y : bool, default=False
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

        assert isinstance(simulation_number, (int, list)), \
            "simulation_number must be either an int or a list of ints"
        
        if isinstance(simulation_number, int):
            simulation_number = [simulation_number]
        if simulation_number == [-1]:
            simulation_number = range(18)
        
        all_images = []
        all_energies = []

        if len(simulation_number) < 2:
            progress_bar = simulation_number
        else:
            progress_bar = tqdm(simulation_number, total=len(simulation_number), leave=False)

        for n in progress_bar:
            zip_file = join(MDS3.p, f"images_{n}.zip")
            csv_file = join(MDS3.p, f"labels_{n}.csv")

            images, energies = get_CahnHilliard_images_and_energies(zip_file, csv_file, verbose)
            all_images += images.tolist()
            all_energies += energies
            
        all_images = np.array(all_images, dtype=int)
        all_energies = np.array(all_energies, dtype=float)

        # mask = np.array(all_energies) <= 1100
        # all_images = all_images[mask]
        # all_energies = all_energies[mask]
        
        # just some sanity checks
        assert all_images[0].shape == MDS3.pixels, f"The images in the zip files should be {MDS3.pixels}  in size"

        feature_names = ['array']
        label_names = ['energy']
        combined_frame = []

        if as_frame:
            X = pd.DataFrame(data=all_images, columns=feature_names)
            y = pd.DataFrame(data=all_energies, columns=label_names)
            combined_frame = pd.concat([X, y], axis=1)
            
        if return_X_y:
            return all_images, all_energies
    
        return Bunch(
            feature_matrix=all_images,
            data=all_images,
            target=all_energies,
            feature_names=feature_names, 
            target_names=label_names, 
            frame = combined_frame,
            DESCR=DESCR,
        )


def load_CahnHilliard(simulation_number=-1):
    """Returns features (the images) and targets (energies)
        
    See `MDS3.load_data` for more information

    :param simulation_number:  if given (as int or list of ints), then only these 
            simulations will be read. Otherwise, all 18 simulations will be read
            and returned.
    """
    images, energies = MDS3.load_data(simulation_number=simulation_number, return_X_y=True)

    return images, energies