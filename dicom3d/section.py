import numpy as np

# internal
from .geometry import *
from .data import walk_data
from .series import Series

class Section():

	""" 
		This class manages a section of the volumetrical scan, able to produce
		a planar image of the datasets intersecting it 

		Examples:
			To build a section, you can use: 
				>>> section = Section.from_plane(series, plane, origin)

			To get the image corresponding wiith this section:
				>>> section.image() 

			To use the local coordinate system:
				>>> point = section.to_mm(x,y)
				>>> x,y = section.to_pixel(point)  
	"""

	def __init__(self, series, coordinateMapping):
		self.series    = series
		self.transform = coordinateMapping

	@staticmethod
	def from_plane(series, plane, origin, orientation=True):
		"""
		Creates a section from a **dicom3d.Plane** and an origin point that will act
		as section's center
		
		Args:
			series (Series): a **dicom3d.Series** object
			plane (Plane): plane definition for this section
			origin (Point, tuple): section's center point in world coordinates 
			orientation (bool, optional): Fixes orientation. Defaults to True.
		
		Raises:
			Exception: when intersection errors are detected
		
		Returns:
			Section: constructed section object 
		"""
		_,_,oz = origin

		# find dataset that interesects origin
		dataset = series.at_z(oz)
		if dataset is None:
			raise Exception("origin (%s) doesn't intersect any dataset" % (origin))

		if plane.parallel(dataset.plane()):

			# just copy X,Y from dataset
			x_vector  = dataset.transform.x_vector.copy()
			y_vector  = dataset.transform.y_vector.copy()

		else:
			# get interesection points with the given plane
			points = dataset.plane_intersection(plane)
			if points is None:
				raise Exception("dataset at origin does not intersect plane")

			if len(points) != 2:
				raise Exception("number of intesection points is invalid (%d)" % (len(points)))

			# select any point from dataset intersection
			point = points[0]

			# construct X and Y axes
			# Note: Y axis is actually the X vector rotated 90 degrees
			normal   = Vector.from_plane(plane)
			x_vector = Vector.from_coords(origin, point).unit()
			y_vector = x_vector.rotate_by_vector(normal,radians(90))

			# make sure X,Y vector has the same orientation, disregarding slice
			if orientation:
				orx = Vector(1,1,0)
				ory = Vector(0,0,1)

				if x_vector.dot(orx) < 0:
					x_vector = x_vector.invert()

				if y_vector.dot(ory) < 0:
					y_vector = y_vector.invert()

				if y_vector.k > 0:
					y_vector = y_vector.invert()

		#print("X: %s Y: %s" % (x_vector, y_vector))
		return Section(series, LocalCoordinateSystem(
				origin,
				x_vector, y_vector, 
				scaling = dataset.PixelSpacing 
			))

	@staticmethod
	def from_dataset(dataset):
		"""
		Constructs a section from a single DICOM dataset

		Args:
			dataset (Dataset): planar DICOM dataset
			origin (): world coordinates of section center

		Returns:
			Section: constructed section object

		Important:
			This function will construct a pseudo-series which will contain
			a single dataset. The pseudo-series can be accesses via *series*
			class member

			>>> section = dicom3d.Section.from_dataset(dataset)
			>>> series = section.series
			>>> series.count()
			1
			>>> series.first() == series.last()
			True
		"""
		# construct single-dataset series
		series = Series.from_dataset(dataset)
		dataset = series.first()

		# borrow dataset's coordinate system
		lcs = dataset.transform.copy()
		lcs.origin = dataset.center()
		lcs.update()
		return Section(series, lcs)

	def _set_pixelspacing(self,v): 
		self.transform.scaling = v
		self.transform.update()

	def _get_pixelspacing(self): 
		return self.transform.scaling

	def _set_density(self,v): 
		dx, dy = v
		self.transform.scaling = (1.0/dx, 1.0/dy)
		self.transform.update()

	def _get_density(self): 
		psx, psy = self.transform.scaling
		return (1.0/psx, 1.0/psy)

	def _set_dpi(self,v): 
		dx, dy = v
		self.transform.scaling = (dx / 25.4, dy / 25.4)
		self.transform.update()

	def _get_dpi(self): 
		psx, psy = self.transform.scaling
		return (psx*25.4, psy*25.4)

	pixel_spacing = property(_get_pixelspacing, _set_pixelspacing)
	"""
	Property describing the distance in millimeters between section's pixels 
	
	Returns:
		tuple: a *tuple* of floats describing the X and Y spacing
	"""

	pixel_density = property(_get_density, _set_density)
	"""
	It is the opposite of the **pixel_spacing** property and describes
	how many pixels are per square millimeter. 
	
	Returns:
		tuple: a *tuple* of floats representing the density on X and Y axis
	"""

	dpi 		  = property(_get_dpi, _set_dpi)
	"""
	Dots per inch property. Similar with **pixel_density** propery, except that 
	it calculates the density per square inch, not per millimeter.
	
	Returns:
		tuple: a *tuple* of floats representing the density on X and Y axis
	"""

	def to_mm(self, x, y):
		"""
		Converts the local pixel coordinates to world coordinates in millimeter units 
		
		Args:
			x (int): value on the X axis
			y (int): value on the Y axis
		
		Returns:
			Point: transformed three-dimensional point representing world coordinates 
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
		return (int(x),int(y))

	def _line(self, image, line_y, offset, max_width):

		ox, oy = offset

		start = self.to_mm(0 + ox, line_y + oy)
		end   = self.to_mm(max_width + ox, line_y + oy)

		sx,sy,sz = start
		ex,ey,ez = end
		ix,iy,iz = (ex-sx)/max_width, (ey-sy)/max_width,(ez-sz)/max_width

		dataset = self.series.at_z(sz)
		if dataset is None:
			return

		pixarr  = dataset.pixel_array
		line_array = image[line_y]

		for i in range(0,max_width):

			x, y = dataset.to_pixel((sx,sy,sz))

			# next pixel
			sx, sy, sz = sx + ix, sy + iy, sz + iz

			# out of range
			if x < 0 or x >= dataset.Columns: continue
			if y < 0 or y >= dataset.Rows   : continue

			if dataset.intersects_z(sz) == False: 
				dataset = self.series.at_z(sz)
				if dataset is None:
					return # out of Z bounds
				pixarr  = dataset.pixel_array

			# copy pixel
			line_array[i] = pixarr[y,x]

		return 

	def image(self, size):
		"""
		Constructs the image corresponding to this section and return an numpy array,
		describing the image
		
		Args:
			size (tuple): tuple of float or integer width,height values (see notes)
		
		Raises:
			ValueError: when input of unknown type is received
			Exception: on intersection errors

		Note:
			If the **size** argument is a tuple of integers, then it will be treated as
			width and height in pixels of the resulting image. 
			If it's a tuple of floats, then it will be considered to be the width and height
			in millimeters for each for the area covered by the resulting image. 
		
		Returns:
			numpy.array: numpy array of the constructed image
		"""

		width, height = size

		if type(width) == float and type(height) == float:
			# size is in millimeters -> convert to pixels

			# move origin right and up
			origin    = self.transform.origin
			far_right = origin.move(self.transform.x_vector, width)
			far_up    = origin.move(self.transform.y_vector, height)

			# convert to pixel and measure lengths
			frx,fry  = self.to_pixel(far_right)
			fux,fuy  = self.to_pixel(far_up)

			dx = np.sqrt(frx ** 2 + fry ** 2)
			dy = np.sqrt(fux ** 2 + fuy ** 2)

			# normalise
			max_lines, max_width = abs(int(dx)), abs(int(dy))

		elif type(width) == int and type(height) == int:
			# size is in pixels
			max_lines, max_width = size
		else:
			raise ValueError(
				"Unknown section image size type (%s) need tuple of floats or integers" % (type(size)))

		# move the (0,0) origin to top-left
		offset = (-max_width//2, -max_lines//2)

		# preallocate
		image = np.zeros((max_lines, max_width), dtype=np.long)

		# populate
		for line in range(0,max_lines):
			self._line(image, line, offset, max_width)

		return image