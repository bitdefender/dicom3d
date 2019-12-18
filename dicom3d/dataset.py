import os

# internal
from .geometry import Point, Plane, Vector, LocalCoordinateSystem
from .data import walk_data

class Dataset():
	""" 
		Wrapper class over the **pydicom.dataset.Dataset** class that provides 
		additional methods for manipulating a dataset, including a local coordinate
		system to map pixel locations over world coordinates	
	"""

	def __init__(self, dataset, series, index):
		self.dataset   = dataset
		self.series    = series
		self.index     = index

		# construct local coordinate system
		xx, xy, xz, yx, yy, yz = dataset.ImageOrientationPatient
		x_vector = Vector(xx,xy,xz)
		y_vector = Vector(yx,yy,yz)

		self.transform = LocalCoordinateSystem(
				dataset.ImagePositionPatient,
				x_vector, y_vector,
				dataset.PixelSpacing
			)

		# accurate Z location to use instead of SliceLocation 
		_,_,self._ZLocation = self.to_mm(0,0)

	def _getZ(self): return self._ZLocation
	ZLocation = property(_getZ)
	"""
	Property describing dataset's Z coordinate in world space in millimeters units 

	Attention:
		According to DICOM standard the *SliceLocation* attrbute is defined as: 
		
		**The relative position of the image plane expressed in mm. This information 
		is relative to an unspecified implementation specific reference point.**

		This makes *SliceLocation* attribute unreliable for ordering or finding datasets
		in world space, as it's possible to indicate a Z coordinate not related to the one
		obtained via dataset's *LocalCoordinateSystem*, thus not related to the *ImagePositionPatient*
		standard attribute.

	Returns:
		float: Z coordinate
	
	Examples:
		>>> # will return pydicom's SliceLocation attribute value
		>>> series.first().SliceLocation 
		"205.7"
		>>> # will return dicom3d.Dataset's attribute
		>>> series.first().ZLocation 
		-205.7
		>>> # notice the dataset's value of Z coordinate for the center point
		>>> # which is obtained via 'ImagePositionPatient' attribute
		>>> series.first().center() 
		x:-2.65 y:-184.74 z:-205.70
	"""

	def to_mm(self, x, y):
		"""
		Converts the local pixel coordinates to world coordinates measured 
		in units of millimeters 
		
		Args:
			x (int): value on the X axis
			y (int): value on the Y axis
		
		Returns:
			Point: transformed three-dimensional point representing world coordinates 

		Examples:
			>>> dataset = series.first()
			>>> pt1 = dataset.to_mm(10,10)   # world coords for pixel at ( 10, 10)
			>>> pt2 = dataset.to_mm(100,100) # world coords for pixel at (100,100)
			>>> print("Distance from pixel (10,10) to (100,100) is %.1f mm" % (
					pt1.distance(pt2)))
			Distance from pixel (10,10) to (100,100) is 89.2 mm
		"""
		return self.transform.to_world(x,y)

	def to_pixel(self, coords):
		"""
		Converts the given point from world coordinates in millimeter units, 
		to local coordinates, in pixels. 
		
		Args:
			coords (tuple, Point): point describing world coordinates
		
		Returns:
			tuple: transformed two-dimensional point representing local coordinates
		"""
		x,y = self.transform.to_local(coords)
		return (int(x), int(y))

	def center(self):
		"""
		Returns the center of the dataset in world coordinates measured in 
		millimeter units
		
		Returns:
			Point: center of the dataset
		"""
		x,y = self.Rows/2, self.Columns/2
		return self.to_mm(x, y)

	def plane(self):
		"""
		Constructs a plane corresponding to this dataset
		
		Returns:
			Plane: plane object

		Examples:
			>>> # plane equation for first dataset 
			>>> series.first().plane()
			0.00X + 0.00Y + 1.00Z = -296.70
		"""
		ox,oy,oz = self.center()
		return Plane.from_coords((ox,oy,oz),(ox,oy,oz+1.0))

	def topleft(self):
		"""
		Returns the corresponding world coordinates for the local (0,0) point
	
		Returns:
			Point: top-left point in world coordinates

		Examples:
			>>> first = series.first()
			>>> first.topleft()
			x:-182.15 y:-364.24 z:-296.70
			>>> # one way of getting dataset's width in millimeters
			>>> first.topleft().distance(first.topright())
			358.298828125
		"""
		return self.to_mm(0, 0)

	def topright(self):
		"""
		Returns the corresponding world coordinates for the local (Columns-1,0) point
		
		Returns:
			Point: top-right point in world coordinates
		"""
		return self.to_mm(self.Columns-1, 0)

	def bottomleft(self):
		"""
		Returns the corresponding world coordinates for the local (0, Rows-1) point
		
		Returns:
			Point: bottom-left point in world coordinates
		"""
		return self.to_mm(0, self.Rows-1)

	def bottomright(self):
		"""
		Returns the corresponding world coordinates for the local 
		(Columns-1, Rows-1) point
		
		Returns:
			Point: bottom-right point in world coordinates
		"""
		return self.to_mm(self.Columns -1, self.Rows-1)

	def prev(self):
		"""
		Returns the previous dataset from the series it belongs to, or None 
		if first
		
		Returns:
			Dataset: previous dataset object

		Examples:
			>>> # one way of navigating backwards through datasets
			>>> dataset = series.last()
			>>> while(dataset is not None):
			>>>		dataset = dataset.prev()
		"""
		if self.index == 0: return None
		return self.series.at_index(self.index-1)

	def next(self):
		"""
		Returns the next dataset from the series it belongs to, or None 
		if last
		
		Returns:
			Dataset: next dataset object

		Examples:
			>>> # one way of navigating forward through datasets
			>>> dataset = series.first()
			>>> while(dataset is not None):
			>>>		dataset = dataset.next()
		"""
		if self == self.series.last(): return None
		return self.series.at_index(self.index+1)

	def intersects_xy(self, xy):
		""" checks if this dataset intersects X,Y world coordinates """
		xs,ys,_ = self.topleft()
		xe,ye,_ = self.bottomright()
		x,y     = xy

		return x <= xe and x >= xs and y <= ye and y >= ys

	def intersects_z(self, z_loc):
		""" checks if this dataset intersects a given Z coordinate """
		return z_loc >= self.ZLocation and z_loc < self.ZLocation + self.SliceThickness

	def intersects_point(self, pt):
		"""
		Verifies if this dataset intersects a given point in world coordinates
		
		Args:
			pt (Point, tuple): point or tuple describing world coordinates
		
		Returns:
			bool: True point intersects dataset, False otherwise
		"""
		x,y,z = pt
		return self.intersects_z(z) and self.intersects_xy((x,y))

	def intersects(self, what):
		""" 
		Checks if the given parameter intersects the dataset

		The first positonal parameter, can be of type:
			- float - which is considered to be a Z coordinate
			- tuple - which is considered to be a (x,y) coordinate
			- plane - plane object

		Args:
			what (float, Point, tuple, Plane): object to test intersection against

		Returns:
			bool: True if intersection was detected or False otherwise

		Examples:
			>>> # check intersection with a Z world coordinate
			>>> dataset.intersects(10.0)
			>>> # check intersection with (X,Y) world coordinate
			>>> dataset.intersects((10.0,30.0))
			>>> # check intersection with a fully-defined point
			>>> dataset.intersects((10.0, 30.0, 10.0))
			>>> dataset.intersects(dicom3d.Point(10,30,10)) # same effect
			>>> # check intersection with a given plane
			>>> dataset.intersects(dicom3d.Plane.from_axes("xy"))
		"""
		if type(what) is float: 
			return self.intersects_z(what)
		
		if type(what) is tuple: 
			if len(what) == 2: return self.intersects_xy(what)
			if len(what) == 3: return self.intersects_point(what)
			raise ValueError("invalid point")

		if type(what) is Point:
			return self.intersects_point(what)	

		if type(what) is Plane: 
			return self.plane_intersection(what) != None

		raise ValueError("invalid argument for intersection")


	def plane_intersection(self, plane):
		
		"""
		Verifies intersection of this dataset with a given plane and returns
		a list of two far-most points on the sides of the dataset, where it 
		touches the plane.
		
		Returns:
			[list]: list of two **dicom3d.Point** objects
		"""

		p = plane # shortcut

		# get world coordinates for this dataset
		zd = self.ZLocation
		oxs,oys,_ = self.topleft()
		oxe,oye,_ = self.bottomright()

		# get extreme points (xs,ys) -> (xe,ye)
		xs, xe = min(oxs, oxe), max(oxs, oxe)
		ys, ye = min(oys, oye), max(oys, oye)

		int_points = []
		int_points.append( p.resolve((oxs,None,zd)) )
		int_points.append( p.resolve((None,oys,zd)) )
		int_points.append( p.resolve((oxe,None,zd)) )
		int_points.append( p.resolve((None,oye,zd)) )

		# clear unresolved, outbound or identical points
		int_final = set()
		for pt in int_points:
			x,y,_ = pt
			if x is None or y is None or \
			   x < xs or x > xe or \
			   y < ys or y > ye:
				continue # out of slice boundaries

			int_final.add((x,y))

		if len(int_final) != 2:
			return None

		(xe,ye),(xs,ys) = int_final
		return [Point(xs,ys,zd), Point(xe,ye,zd)]


	def __getattr__(self,name):
		""" redirect other atribute requests to the pydicom class """
		return self.dataset.__getattr__(name)

