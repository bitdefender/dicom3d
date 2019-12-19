import setuptools

_long_description_ = """
**dicom3d** is a comprehensive Python package for reconstructing arbitrary defined 3D sections 
from volumetric medical scans (CTs or RMNs), scale accurate and with a builtin pixel-to-world 
coordinate mapping system.

It comes preloaded with the necessary mathematical backend to manipulate space information from 
medical scans, and provides a mapping system that can transparently handle different imaging 
properties such as pixel density, dataset thickness, patient orientation, patient positioning, 
etc.

Dependencies
------------
It relies on **pydicom** for loading DICOM medical images and **numpy** for array manipulation.

Repository
----------

For source code and documentation visit [dicom3d](https://github.com/bitdefender/dicom3d) **GitHub** repository

Installation
------------

From **PyPi** package repository:

    pip install dicom3d

License
-------
Licence for this Python package is the **MIT License** under **Copyright (c) 2020 Bitdefender**.

Author
-------
Developed and maintained by *Alex Mircescu* (`amircescu`@`bitdefender.com`)
"""

_description_ = \
    "Library for reconstructing arbitrary defined 3D sections" \
    "from volumetric medical scans"

setuptools.setup(
    name="dicom3d",
    version="0.9.8",
    author="Alex Mircescu",
    author_email="mircescu@gmail.com",
    description= _description_,
    long_description= _long_description_,
    long_description_content_type="text/markdown",
    url="https://github.com/bitdefender/dicom3d",
    packages=setuptools.find_packages(),
    keywords = [ 
        'python', 
        'medical', 'rmn', 'ct', 
        'dicom', 'reconstruction', 'imaging'
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries"
    ],
    install_requires= [
        'pydicom', 'numpy'
    ],
    python_requires='>=3.4',
)