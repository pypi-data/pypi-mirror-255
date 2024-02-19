import copy
import os

from tqdm import tqdm

from fast_skimage import Image
import warnings
import matplotlib.pyplot as plt
import numpy as np
from random import randrange

class Collection():
    """
    The Collection class is designed to handle multiple images (through the Image class) and find common properties

    Designed by Alexandre Le Mercier on the 7th of February 2024
    """
    def __init__(self, image_list=None, name="", need_format_consistency=True, need_dimension_consistency=True,
                 verbose=1, directory_path=None):
        self.init_name(name)
        self.images = dict()
        self.size = 0
        self.format = (0, 0)  # Should be updated
        self.iscolor = False  # Should be updated
        self.format_consistency = True
        self.dimension_consistency = True
        self.warn_format_inconsistency = need_format_consistency
        self.warn_dimension_inconsistency = need_dimension_consistency
        self.verbose = verbose

        if directory_path is not None:
            self.load_images_from_directory(directory_path)
        elif image_list is not None:
            self.init_collection(image_list)
        else:
            warnings.warn(""
                          "No images or directory path provided, empty collection created.")

    def __add__(self, other):
        if type(other) == Image:
            self.add_image(other)
        elif type(other) == Collection:
            for im in other.images:
                self.add_image(im)
        else:
            raise ValueError(f"Cannot add a collection with object of class \"{type(other)}\".")

    def add_image(self, im):
        """
        Add a new image to the collection
        """
        if type(im) == Image:
            self.images[self.size] = im
        else:
            warnings.warn(""
                          "The image you are trying to upload is not in the library's \"fast_skimage.Image\" class. "
                          "We will try to convert it into an \"Image\" object.")
            new_im = Image(im)
            if type(new_im) == Image:
                self.images[self.size] = new_im
                if self.verbose:
                    print("The image was successfully converted into a fast_skimage.Image object !")
        self.update_collection()

    def check_dimension_consistency(self):
        """
        Verifies that all the images within the collection or either all grayscale or all colored.
        This is not a mandatory criterion, but dimension inconsistency may lead to undesired effects.
        """
        if self.dimension_consistency:
            was_consistent = True
        else:
            was_consistent = False
            self.dimension_consistency = True

        if self.size > 1:
            im0 = next(iter(self.images.values()))  # Get the first image from the dictionary
            iscolor = im0.iscolor
            for (key, image) in self.images.items():
                if image.iscolor != iscolor:
                    self.dimension_consistency = False
                    if was_consistent and self.warn_dimension_inconsistency:
                        warnings.warn(f""
                                      f"In collection {self.name}, image at key {key} just brought dimension"
                                      f" inconsistency.")
                    elif self.verbose > 1:
                        f"Collection {self.name} has dimension inconsistency!"
                else:
                    self.iscolor = iscolor

    def check_image_format_consistency(self):
        """
        Verifies that all the images within the collection have the same format.
        This is not a mandatory criterion, but format inconsistency may lead to undesired effects.
        """
        if self.format_consistency:
            was_consistent = True
        else:
            was_consistent = False
            self.format_consistency = True

        if self.size > 1:
            im0 = next(iter(self.images.values()))  # Get the first image from the dictionary
            width = im0.width
            height = im0.height
            for (key, image) in self.images.items():
                if image.height != height or image.width != width:
                    self.format_consistency = False
                    if was_consistent and self.warn_format_inconsistency:
                        warnings.warn(f""
                                      f"In collection {self.name}, image at key {key} just brought format"
                                      f" inconsistency.")
                    elif self.verbose > 1:
                        f"Collection {self.name} has format inconsistency!"
                else:
                    self.format = (im0.width, im0.height)

    def copy(self):
        """
        Copy the actual Collection into another Collection object
        """
        return copy.deepcopy(self)

    def get_iterable(self, iterable):
        return tqdm(iterable) if self.verbose > 0 else iterable

    def init_collection(self, images):
        """
        Creates the image collection when the Collection object is created.
        """
        print(images)
        self.format = (images[0].width, images[0].height)  # Assumes format consistency
        self.iscolor = (images[0].iscolor) # Assumes dimension consistency
        for im in self.get_iterable(images):
            self.add_image(im)
        if self.verbose > 0:
            if self.format_consistency:
                if self.dimension_consistency and self.iscolor:
                    print(f"Collection {self.name} instantiated. It has {self.size} colored images of format"
                          f" {self.format}.")
                elif self.dimension_consistency and not self.iscolor:
                    print(f"Collection {self.name} instantiated. It has {self.size} grayscale images of format"
                          f" {self.format}.")
                else:
                    print(f"Collection {self.name} instantiated. It has {self.size} images of format {self.format}.")
            else:
                print(f"Collection {self.name} instantiated. It is format-inconsistent.")

    def init_name(self, name):
        """
        Attribute a name to the collection (random by default)
        """
        if name:
            self.name = name
        else:
            self.name = str(randrange(100000))

    def load_images_from_directory(self, directory_path):
        # List all files in the given directory
        for filename in self.get_iterable(os.listdir(directory_path)):
            # Check for JPEG images
            if filename.lower().endswith((".jpg", ".jpeg")):
                img_path = os.path.join(directory_path, filename)
                try:
                    img = Image(img_path)  # Assuming Image can be instantiated with a file path
                    self.add_image(img)  # Assuming add_image is a method that adds an Image object to the collection
                except Exception as e:
                    warnings.warn(f""
                                  f"Failed to load image {filename}: {e}")

    def show_collection(self, type_of_plot='mean', type_of_graph='image', cmap='gray'):
        """
        Show the mean, maximum, minimum, or difference image/histogram of the collection.
        :param type_of_plot: 'mean', 'max', 'min', or 'diff' for the type of calculation
        :param type_of_graph: 'image' or 'hist' to show the image or histogram
        :param cmap: Colormap for grayscale images
        """

        self.check_image_format_consistency()
        self.check_dimension_consistency()

        if self.size < 1:
            raise ValueError("No images in collection to show.")

        # Ensure that the collection has format and dimension consistency
        if not self.format_consistency or not self.dimension_consistency:
            raise ValueError("The collection must have format and dimension consistency to perform this operation.")

        first_image = next(iter(self.images.values()))
        img_shape = self.format
        dtype = first_image.image.dtype

        # Initialize arrays to store the cumulative values
        cumul_image = np.zeros(img_shape, dtype=np.float64)
        max_image = np.zeros(img_shape, dtype=np.float64)
        min_image = np.full(img_shape, np.inf, dtype=np.float64)
        diff_image = np.zeros(img_shape, dtype=np.float64)

        # Iterate over all images to calculate cumulative values
        for im in self.images.values():
            img_data = im.image.astype(np.float64)
            cumul_image += img_data
            max_image = np.maximum(max_image, img_data)
            min_image = np.minimum(min_image, img_data)

        # Calculate the mean image
        mean_image = cumul_image / self.size

        # Calculate the difference image
        for image in self.get_iterable(self.images.values()):
            diff_image += np.abs(image.image.astype(np.float64) - mean_image)

        # Choose the operation to perform
        if type_of_plot == 'mean':
            result_image = mean_image
        elif type_of_plot == 'max':
            result_image = max_image
        elif type_of_plot == 'min':
            result_image = min_image
        elif type_of_plot == 'diff':
            result_image = diff_image
        else:
            raise ValueError("type_of_plot must be 'mean', 'max', 'min', or 'diff'.")

        # Convert result to Image object and use the Image.show method
        result_image_obj = Image(result_image.astype(dtype))
        if type_of_graph == 'image':
            result_image_obj.show(cmap=cmap)
        elif type_of_graph == 'hist':
            plt.axis()
            result_image_obj.show(type_of_plot='hist')
        else:
            raise ValueError("type_of_graph must be 'image' or 'hist'.")

    def update_collection(self):
        """
        Update parameters, and check consistency
        """
        self.size = len(self.images)
        self.check_image_format_consistency()
        self.check_dimension_consistency()
        if self.verbose > 1:
            print(f"Collection \"{self.name}\" updated. It has now {self.size} images.")
