# fast-skimage

Welcome to `fast-skimage`, an image acquisition and processing library. This powerful library offers a wide range of tools for advanced image manipulation and analysis, wrapped up in the accessible `Image` class.

## Features
- **Advanced Manipulation**: Apply complex operations like adding watermarks, noise detection, auto-enhancement, and saturation increase with simple method calls.
- **Filtering and Thresholding**: Includes mean, median filtering, Otsu's thresholding, and custom thresholding methods for image segmentation and noise reduction.
- **Fourier Transforms**: Utilize Fourier-based methods for reducing image dithering and other artifacts.
- **Histogram Operations**: Equalize and stretch image histograms to improve contrast and visibility.
- **Texture Analysis**: Perform texture segmentation using a variety of descriptors.
- **Small Image Library**: 7 various pictures for testing are provided with the package (see section "Image Library" below).

## Getting Started
1. **Installation**: Clone the repository or download the `Image` class module to your project.
2. **Dependencies**: Ensure all dependencies such as `numpy`, `matplotlib`, `scikit-image`, and `PyWavelets` are installed.
3. **Usage**: Import the `Image` class from the module and instantiate it with the path to your image or a NumPy array.

## Example
```python
from fast_skimage import Image
from fast_skimage import etretat
from skimage.data import immunohistochemistry

img = Image("Pictures/camera.jpg")  # Load an image with path...
img2 = Image(immunohistochemistry())  # ... or numpy array ...
colored_image_array = etretat() # ... or a library image.
img3 = Image(colored_image_array.get())

img2.auto_enhance()  # Apply auto-enhancement
img3.auto_enhance()

img3.show(subplots=(1, 2, 1), size=12)  # Display the result
img2.show(subplots=(1, 2, 2), title='Immunochemistry Image')

img.show(size=(12, 6), type_of_plot='hist', axis=True)  # Plot histogram
```

## Image Library
A small image library is provided along with the `Image` class. These can be manually extracted with the following lines:
```python
from fast_skimage import image_name
image_array = image_name()
image = Image(image_array.get())
```
Note that all images listed below come from the INFO-H500 course of Prof. Olivier Debeir at ULB (Université Libre de Bruxelles).

### Grayscale Noisy Image

- `fast-skimage.astronaut_noisy` 

### Grayscale Clean Images

- `fast-skimage.camera`
- `fast-skimage.walking`

### Grayscale Clean Watermark

- `fast-skimage.watermark` (the ULB logo)

### Colored Clean Images

- `fast-skimage.etretat`
- `fast-skimage.nyc`
- `fast-skimage.zebra`

## Documentation
Refer to the in-line comments and method docstrings for detailed usage of each feature.

## Contribution
Contributions are welcome! Feel free to submit pull requests, suggest features, or report bugs.

## License
This library is distributed under the MIT license. See `LICENSE` for more information.

## Contact
- **Author**: Alexandre Le Mercier
- **Date**: November 21, 2023
- **Email**: [alexandre.le.mercier@ulb.be](mailto:alexandre.le.mercier@ulb.be)
- **LinkedIn**: [Alexandre Le Mercier](https://www.linkedin.com/in/alexandre-le-mercier-7b5594283/details/experience/)

Happy Image Processing!