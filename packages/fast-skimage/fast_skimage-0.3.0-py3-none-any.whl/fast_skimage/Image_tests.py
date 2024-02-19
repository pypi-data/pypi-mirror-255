import unittest
from fast_skimage import Image
from fast_skimage import camera
from skimage.data import immunohistochemistry
from fast_skimage.Image import RED, WHITE, BLUE, GREEN

class ImageTestCase(unittest.TestCase):


    def test_get_camera(self):
        """
        img = Image("Pictures/camera.jpg")  # Load an image with path...
        img2 = Image(immunohistochemistry())  # ... or numpy array ...
        my_camera = camera() # ... or a library image.
        img3 = Image(my_camera.get())

        img.auto_enhance()  # Apply auto-enhancement
        img2.auto_enhance()

        img3.show(subplots=(1, 2, 1), size=12)  # Display the result
        img2.show(subplots=(1, 2, 2), title='Immunochemistry Image')

        img.show(size=(12, 6), type_of_plot='hist', axis=True)  # Plot histogram

    def test_add_watermark(self):
        path_to_nyc = 'Pictures/nyc.jpg'
        path_to_watermark = 'Pictures/watermark.png'
        path_to_zebra = 'Pictures/zebra.jpg'

        background_image = Image(path_to_nyc)
        watermark = Image(path_to_watermark)
        watermark2 = Image(path_to_zebra)

        background_image.add_watermark(watermark2, 0.5, 0.5, wm_color=RED, alpha=0.05, spread=0.2)
        background_image.add_watermark(watermark, 0.2, 0.7, wm_color=WHITE, alpha=0.5, spread=1)
        background_image.add_watermark(watermark2, 0.6, 0.1, wm_color=BLUE, alpha=1, spread=0.1)
        background_image.add_watermark(watermark2, 0.3, 0.3, wm_color=GREEN, alpha=1, spread=0.15)
        background_image.show(title="Marked NYC Picture")


    def test_auto_enhance(self):
        path_to_image1 = 'Pictures/zebra.jpg'
        path_to_image2 = 'Pictures/astronaut_noisy.jpg'
        path_to_image3 = 'Pictures/nyc.jpg'
        path_to_image4 = 'Pictures/etretat.jpg'
        path_to_image5 = 'Pictures/walking.jpg'
        path_to_image6 = 'Pictures/camera.jpg'
        path_to_image7 = immunohistochemistry()

        imlist = [Image(path_to_image1), Image(path_to_image2), Image(path_to_image3), Image(path_to_image4),
                  Image(path_to_image5), Image(path_to_image6), Image(path_to_image7)]

        for im in imlist:
            im.show(subplots=(1, 2, 1), size=12, title=im.name + " original")
            im.auto_enhance()
            im.show(subplots=(1, 2, 2), title=im.name + " auto-enhanced")

    def test_texture_segmentation(self):
        im = Image('Pictures/zebra.jpg')

        im.texture_segmentation(patch_size=3)
        im.show(greyscale=True)


    def test_help(self):
        im = Image(immunohistochemistry())
        help(Image)
        #im.help() --> launches the help menu


    def test_show(self):
        # Load an image with path...
        img = Image("Pictures/camera.jpg")
        # ... or numpy array
        img2 = Image(immunohistochemistry())

        # Apply auto-enhancement
        img.auto_enhance()
        img2.auto_enhance()

        # Display the result
        img.show(subplots=(1, 2, 1), size=12)
        img2.show(subplots=(1, 2, 2), title='Immunochemistry Image')

        # Plot histogram
        img.show(size=(12, 6), type_of_plot='hist', axis=True)

"""
    def test_save_data(self):

        path_to_image1 = 'Pictures/zebra.jpg'
        path_to_image2 = 'Pictures/astronaut_noisy.jpg'
        path_to_image3 = 'Pictures/nyc.jpg'
        path_to_image4 = 'Pictures/etretat.jpg'
        path_to_image5 = 'Pictures/walking.jpg'
        path_to_image6 = 'Pictures/camera.jpg'
        path_to_image7 = 'Pictures/watermark.png'

        paths = [
            path_to_image1,
            path_to_image2,
            path_to_image3,
            path_to_image4,
            path_to_image5,
            path_to_image6,
            path_to_image7
        ]

        for path in paths:
            img = Image(path)
            name = path[9:-4]
            with open(name+ ".py", 'w', encoding='utf-8') as file:
                image_list = img.image.tolist()
                string = f'''
import numpy as np
 
class {name}:
    def get(self):
        return np.array({image_list})
'''
                file.write(string)



if __name__ == '__main__':
    unittest.main()