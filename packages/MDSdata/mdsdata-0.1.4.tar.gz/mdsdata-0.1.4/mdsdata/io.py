import zipfile, io
from PIL import Image
import numpy as np
import os.path
import pandas as pd


def assert_that_zip_archive_contains_only_files(filename):
    """Returns True if the zip archive contains only files, otherwise throws an exception.

    :param filename: path and filename of the zip archive
    """
    zip_path = filename

    # Open the ZIP archive for reading
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Get a list of all items (files and directories) in the ZIP archive
        zip_items = zip_ref.infolist()

        # Check if there are only files and no directories in the ZIP archive
        only_files = all(not os.path.isdir(item.filename) for item in zip_items)
        only_directories = all(os.path.isdir(item.filename) for item in zip_items)

        if only_files and not only_directories:
            return True
            #print("The ZIP archive contains only files and no directories.")
        elif only_files and only_directories:
            assert False, "The ZIP archive is empty."
        else:
            assert False, "The ZIP archive contains directories or a combination of files and directories."
        


def read_images_from_zip_archive(zip_filename):
    """Extracts image from a ZIP archive and returns them as a list of image arrays together with the filenames.
    
    :param filename: path and filename of the zip archive
    :return: list of ndarrays, list of filenames (within the zip archive)
    """
    with zipfile.ZipFile(zip_filename) as myzip:
        filenames = myzip.namelist()
        with myzip.open(filenames[0]) as myfile:
            img_data = myfile.read()
            buf = io.BytesIO(img_data)
            img = np.asarray(Image.open(buf))

    list_of_image_arrays = []
    list_of_filenames = []

    with zipfile.ZipFile(zip_filename) as myzip:
        for i, file in enumerate(filenames):
            with myzip.open(file) as myfile:
                list_of_filenames.append(file)
                img_data = myfile.read()
                buf = io.BytesIO(img_data)
                img = np.asarray(Image.open(buf))
                list_of_image_arrays.append(img)

    return list_of_image_arrays, list_of_filenames


def get_Ising_images_temperatures_and_labels(zip_filename, csv_filename, verbose):
    if verbose:
        print("- Reading zip archive from the location:\n ", zip_filename)
    assert_that_zip_archive_contains_only_files(zip_filename)

    images, filenames = read_images_from_zip_archive(zip_filename)
    shape = images[0].shape
    n_images = len(images)

    if verbose:
        print(f"- Extracted {n_images} images with {shape[0]} x {shape[1]} pixel.")
        print("- Reading temperatures and labels from CSV file:\n ", csv_filename)

    csv_dataset = pd.read_csv(csv_filename)
    csv_filenames = csv_dataset['filenames']

    temperatures = []
    labels = []
    for i, filename in enumerate(filenames):
        # make sure that we pick the temperature and label that corresponds
        # to a particular filename from the ZIP archive.
        idx = np.argwhere(csv_dataset['filenames'] == filename)[0][0]
        temperatures.append(csv_dataset['temperatures'][idx])
        labels.append(csv_dataset['labels'][idx])
        # print(idx, filename, csv_filenames[idx])
        # print(temperatures)
    images = np.array(images, dtype=float)

    return images, temperatures, labels


def get_CahnHilliard_images_and_energies(zip_filename, csv_filename, verbose):
    if verbose:
        print("- Reading zip archive from the location:\n ", zip_filename)
    assert_that_zip_archive_contains_only_files(zip_filename)

    images, filenames = read_images_from_zip_archive(zip_filename)
    shape = images[0].shape
    n_images = len(images)

    if verbose:
        print(f"- Extracted {n_images} images with {shape[0]} x {shape[1]} pixel.")
        print("- Reading energies from CSV file:\n ", csv_filename)

    csv_dataset = pd.read_csv(csv_filename)
    csv_filenames = csv_dataset['filenames']

    energies = []
    for i, filename in enumerate(filenames):
        # make sure that we pick the temperature and label that corresponds
        # to a particular filename from the ZIP archive.
        idx = np.argwhere(csv_dataset['filenames'] == filename)[0][0]
        energies.append(csv_dataset['energy'][idx])
    images = np.array(images, dtype=float)

    return images, energies