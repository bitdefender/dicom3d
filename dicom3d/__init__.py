"""
Root **dicom3d** module implementing **Section**, **Series**, **Dataset** class objects
"""

__all__ = [
	"Section",
	"Series",
	"Dataset",
	"Plane",
	"Vector",
	"Point",
	"LocalCoordinateSystem",
	"degrees", 
	"radians",
	"version"
]

version = "0.9.2"

from .dataset import *
from .section import *
from .series import *
from .geometry import *