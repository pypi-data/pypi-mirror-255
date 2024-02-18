from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.3'
DESCRIPTION = 'IDPettis Intrinsic Dimensionality Estimation by Alberto Biscalchin'
LONG_DESCRIPTION = 'This repository contains a Python implementation of the IDPettis algorithm, which is designed to estimate the intrinsic dimensionality of a dataset. The intrinsic dimensionality represents the minimum number of variables required to approximate the structure of the dataset.'

# Setting up
setup(
    name="idPettis_By_Bisca",
    version=VERSION,
    author="Eng. Alberto Biscalchin",
    author_email="biscalchin.mau.se@gmail.com",  
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION, 
    packages=find_packages(),
    install_requires=['numpy', 'scipy'],  
    keywords=['IDPettis', 'intrinsic dimensionality estimation', 'dimensionality reduction', 'data analysis', 'machine learning', 'data science', 'nearest neighbors', 'high-dimensional data', 'dimensionality analysis', 'scientific computing', 'helix dataset', 'pdist', 'scipy', 'numpy', 'matplotlib', 'algorithm'],
    classifiers=[
        "Development Status :: 4 - Beta",  
        "Intended Audience :: Science/Research",  
        "Programming Language :: Python :: 3",  
        "Operating System :: OS Independent",
    ]
)
