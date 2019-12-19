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