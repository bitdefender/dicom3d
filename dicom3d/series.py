import pydicom
import numpy as np

from .dataset import Dataset
from .data import walk_data

class Series():
	"""
	Class responsible for managing a volumetric scan, comprised by a list of successive datasets

	Note:
		When constructed, this class performs the following operations 
			- sorts the given datasets by *ZLocation*
			- wraps the datasets in **dicom3d.Dataset** class
			- checks the series for spacial homogeneity

	Attention:
		Homogeneity check is required by this class to make sure the assumptions 
		it makes over the volumetric scan, are correct. These assumptions are related
		to space contiguity between datasets and consistent density and size among
		datasets 
		
	Important: 
		A series is homogeneous if:
			- all datasets are continuous on the Z axis (no gaps)
			- each dataset has identical values for these attributes
				- SliceThickness 
				- PixelSpacing 
				- Rows
				- Columns
				- ImagePositionPatient
				- ImageOrientationPatient

	"""

	def __init__(self, datasets, check_homogeneity=True):

		# wrao datasets in helper class
		wrapped_datasets = self._wrap(datasets)

		# sort datasets by SliceLocation
		self.datasets = sorted(wrapped_datasets, key=lambda ds: ds.ZLocation)

		# fix index
		for idx, dataset in enumerate(self.datasets):
			dataset.index = idx

		# check for consistency in Z-location, thickness, density etc.
		if check_homogeneity:
			self._verify_homogeneity()
			self._build_mapping()
		else:
			self.homogeneous = False
			self.mapping = None

		self.pixel_data = None

	@staticmethod
	def from_directory(path, pattern="*.dcm", check_homogeneity=True):
		"""
		Constructs a series from a directory of DICOM files
		
		Args:
			path (str): path to the directory continaing the DICOM files
			pattern (str, optional): Wildcard pattern of DIICOM files, default is "\*.dcm"
			check_homogeneity (bool, optional): Homogeneity test, default is **True**
		
		Returns:
			[Series]: a **dicom3d.Series** object
		"""

		# enumerate all files with this pattern
		files = walk_data(
			path, pattern, 
			search_files=True, search_dirs=False)

		# read the datasets
		datasets = [ pydicom.dcmread(image_filename)
							 	 for image_filename in files ]
					
		if len(datasets) == 0:
			raise Exception("no datasets found to build series from directory '%s'" % (
				path ))

		# construct the series
		return Series(
			datasets,
			check_homogeneity = check_homogeneity)

	@staticmethod
	def from_dataset(dataset):
		"""
		Constructs a series from a single dataset. Helpful if you want to build
		section images from planar datasets
		
		Args:
			dataset (Dataset): planar DICOM dataset
		
		Returns:
			Series: resulted series object
		"""
		series = Series([dataset])
		series.homogeneous = True
		return series

	@staticmethod
	def fix_z_duplicates(datasets):
		"""
		Attempts to curate a list of datasets that has datasets duplicated on the Z axis
		
		Args:s
			datasets (list): list of pydicom.dataset.Dataset objects

		Important:
			This code is experimental and is used to fix some series that fail the
			homogeneity test.
		"""

		# construct a set of SliceLocations
		locations_set = { ds.SliceLocation for ds in datasets }

		# if the number of locations is lower than the number of datasets
		# => dataset list has duplicated elements in regards of SliceLocation 
		if len(locations_set) != len(datasets):

			curated = []

			# eliminate those datasets with duplicated SliceLocation
			for ds in datasets:

				# if in unique location list, add to curated
				# if not, it's a duplicate dataset
				if ds.SliceLocation in locations_set:
					curated.append(ds)
					locations_set.remove(ds.SliceLocation)

			return curated

		# the original list has no duplicates
		return datasets

	def _wrap(self, datasets):
		""" wrap each dataset into the 'dataset' class """

		if len(datasets) == 0:
			return []

		# already wraped, re-wrap
		if type(datasets[0]) is Dataset:
			return [ Dataset(x.dataset, self, idx) 
					for idx,x in enumerate(datasets) ]

		return [ Dataset(x, self, idx) 
					for idx,x in enumerate(datasets) ]

	def _build_mapping(self):

		# avoid using SliceThickness
		if len(self.datasets) > 1:
			thick = self.datasets[1].ZLocation - self.datasets[0].ZLocation
		else:
			thick = self.datasets[0].SliceThickness

		start_z = self.first().ZLocation
		end_z   = self.last().ZLocation + thick

		self.mapping = (start_z, end_z, thick)
		return True

	def _ensure_homogeneity(self):
		if self.homogeneous == False: 
			raise ValueError("series must be homogeneous to use this function")

	def _verify_homogeneity(self, tolerance=1.e-4):
		"""
			checks if the given series of datasets is continuous (i.e. each
			dataset starts where the previous dataset ends) and also checks
			if all datasets have the same thinkness
		"""

		# single dataset series
		if len(self.datasets) == 1:
			self.homogeneous = True
			return

		# check continuity
		prev = self.first()

		ref_thickness = prev.SliceThickness
		ref_distance  = prev.next().ZLocation - prev.ZLocation
		ref_Rows      = prev.Rows
		ref_Columns   = prev.Columns 
		ref_imop	  = prev.ImageOrientationPatient
		ref_density   = prev.PixelSpacing

		if ref_distance == 0:
			raise Exception("homogeneity test failed: first datasets have the same Z location")
		
		for dataset in self.datasets[1:]:

			# check if a datasets ends where the other one begins
			diff = dataset.ZLocation - prev.ZLocation - ref_distance
			if abs(diff) > tolerance:
				raise Exception("homogeneity test failed: series is not continuous on the Z axis")

			# check if a dataset has different slice thickness
			if dataset.SliceThickness != ref_thickness:
				raise Exception("homogeneity test failed: series has datasets with variable thickness")

			# check for same rows and columns
			if dataset.Rows != ref_Rows or dataset.Columns != ref_Columns:
				raise Exception("homogeneity test failed: series has datasets with variable Rows,Columns configuration")

			# datasets must have same coordinate system
			if dataset.ImageOrientationPatient != ref_imop:
				raise Exception("homogeneity test failed: series has datasets with different orientation (ImageOrientationPatient)") 

			# datasets must have same density
			if dataset.PixelSpacing != ref_density:
				raise Exception("homogeneity test failed: series has datasets with different density (PixelSpacing)")

			prev = dataset

		self.homogeneous = True
		return

	def cache(self):
		"""
		Builds a three-dimensional numpy array from all pixel data from datasets. 
		
		Important:
			Reserved for future use!

		Returns:
			numpy.array: numpy array of the pixel data
		"""

		if self.pixel_data is not None:
			return self.pixel_data

		self._ensure_homogeneity()

		dataset    = self.first()
		zd, yd, xd = len(self.datasets), dataset.Rows, dataset.Columns
		pixel_data = np.zeros((zd, yd, xd),dtype=np.long)

		# populate
		for zi, dataset in enumerate(self.datasets):
			pixel_data[zi,:,:] = dataset.pixel_array

		self.pixel_data = pixel_data
		return pixel_data


	def first(self):
		"""
		Retrives the first dataset from series. The first dataset is located at the bottom 
		of the Z segment, therefore it will have the lowest Z coordinate value.
		
		Returns:
			Dataset: a **dicom3d.Dataset** object
		"""
		return self.datasets[0]

	def last(self):
		"""
		Retrives the last dataset from series. The last dataset is located at the top 
		of the Z segment, therefore it will have the highest Z coordinate value.
		
		Returns:
			Dataset: a **dicom3d.Dataset** object
		"""
		return self.datasets[len(self.datasets) -1]

	def middle(self):
		"""
		Retrives the dataset from series that is on the middle of the Z segment. 
		
		Returns:
			Dataset: a **dicom3d.Dataset** object
		"""
		return self.datasets[len(self.datasets)//2]

	def count(self):
		"""
		Returns the number of datasets
		
		Returns:
			int: legnth of datasets list 
		"""
		return len(self.datasets)

	def z_bounds(self):
		"""
		Returns a tuple representing the world Z coordinates of the volumetric scan, 
		including the top dataset and its thickness.

		Important:
			If homogeneity test was disabled for this series, this function will raise
			an exception

		Returns:
			tuple: a tuple of float values representing the Z bounds
		
		Examples:
			>>> z_start, z_end = series.z_bounds()
			>>> print("Series starts from %.1f to %.1f mm on the Z axis" % (z_start, z_end) )
		"""
		
		self._ensure_homogeneity()

		start_z, end_z, _ = self.mapping
		return (start_z, end_z)

	def at_index(self, index):
		"""
		Returns the dataset at the corresponding index or None if index is out of bounds.
		
		Args:
			index (int): dataset index in series
		
		Returns:
			Dataset: the **dicom3d.Dataset** object at **index**  
		"""
		if index < 0 or index > len(self.datasets):
			return None # exceeds list

		return self.datasets[index]

	def at_z(self, z_loc):
		"""
		Returns the dataset that intersects the given Z location in world coordinates
		
		Important:
			If homogeneity test was disabled for this series, this function will raise
			an exception

		Args:
			z_loc (float): value describing location on the Z axis

		Returns:
			Dataset: the corresponding **dicom3d.Dataset** object 
		"""
		self._ensure_homogeneity()

		# linear mapping -> calculate index
		start_z, end_z, thick = self.mapping
		if z_loc >= end_z or z_loc < start_z: 
			return None # exceeds Z segment

		idx = int((z_loc - start_z) / thick)
		return self.datasets[idx]

	def at(self, where):
		"""
		This is a wrapper function for ease of use over **at_index** and
		**at_z** functions.

		Args:
			where (int, float, tuple, Point): if **where** is an integer is treated like an index,
				else is considered to be a Z location

		Returns:
			Dataset: the corresponding **dicom3d.Dataset** object 

		Examples:
			 >>> dataset = series.at(1.0) # gets dataset at 0.1 Z coordinate
			 >>> dataset = series.at(1)   # gets dataset at index 1
			 >>> dataset = series.at(Point(5,5,2)) # gets dataset at 2.0 Z coordinate
		"""

		if type(where) is int:
			return self.at_index(where)
		if type(where) is float:
			return self.at_z(where)
		if type(where) is tuple and len(where) == 3 or type(where) is Point:
			x,y,z = where
			dataset = self.at_z(z)
			if dataset is None: return None
			return dataset if dataset.intersects_xy((x,y)) else None

		raise ValueError("invalid type for looking up dataset (%s)" % (type(where)))

	def find_dataset(self, z_loc):
		"""
		Despite **Series.at_z** method, this one doesn't require homogenuity test to be ran
		If will effectively search though the list to find the corresponding dataset, instead
		of calculating the index based on Z-bounds and dataset thickness.
		
		Args:
			z_loc (float):  value describing location on the Z axiss 
		
		Returns:
			int: index of the corresponding dataset or -1 if not found
		"""
		for idx, dataset in enumerate(self.datasets):
			if z_loc >= dataset.ZLocation and z_loc < dataset.ZLocation + dataset.SliceThickness:
				return idx
		return -1 
