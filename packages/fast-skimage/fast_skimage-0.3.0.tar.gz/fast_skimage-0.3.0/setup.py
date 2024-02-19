# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="fast_skimage",
    version="0.3.0",
    description="Fast and easy image processing using an Image class based on the scikit-image,"
                " numpy and matplotlib libraries.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TortueSagace/fast_skimage",
    author="Alexandre Le Mercier",
    author_email="alexandre.le.mercier@ulb.be",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=["fast_skimage"],
    include_package_data=True,
    install_requires=["numpy", "matplotlib", "scikit-image", "PyWavelets", "tqdm", "scikit-learn"]
)

"""
python setup.py sdist bdist_wheel
twine check dist/*
twine upload dist/*
"""