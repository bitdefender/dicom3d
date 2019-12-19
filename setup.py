import setuptools
import sys
import os

DICOM3D_PATH = os.path.abspath("./dicom3d")
sys.path.append(DICOM3D_PATH)

from dicom3d import version

with open("README_PYPI.md", "r") as fh:
    _long_description_ = fh.read()

_description_ = \
    "Library for reconstructing arbitrary defined 3D sections" \
    "from volumetric medical scans"

setuptools.setup(
    name="dicom3d",
    version=version,
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