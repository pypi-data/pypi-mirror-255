from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.2'
DESCRIPTION = 'Python module for dimensionality analysis using CorrDim and related algorithms'
LONG_DESCRIPTION = (
    'This Python module provides robust methods for estimating the Correlation Dimension '
    'of any given dataset, leveraging the CorrDim algorithm, and includes additional '
    'functions such as packing_numbers and local_dim for comprehensive '
    'dimensionality analysis. Suitable for applications in fractal dimensions, '
    'chaos theory, and complex data analysis.'
)

# Setting up
setup(
    name="CorrDim_By_Bisca",
    version=VERSION,
    author="Eng. Alberto Biscalchin",
    author_email="biscalchin.mau.se@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy', 'scipy'],
    keywords=[
        "correlation dimension", "CorrDim algorithm", "fractal analysis", "chaos theory",
        "data analysis", "NumPy", "SciPy", "multidimensional scaling",
        "time-series analysis", "packing numbers", "local dimension"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)
