import numpy as np
from numpy.linalg import norm

def degrees(radians):
	"""
	Converts the given angle from radians to degrees
	
	Args:
		radians (float): angle in radians
	
	Returns:
		float: resulting angle in degrees
	"""
	return np.degrees(radians)

def radians(degrees):
	"""
	Converts a given angle from degrees to radians
	
	Args:
		degrees (float): angle in degrees
	
	Returns:
		float: resulting angle in radians
	"""
	return np.radians(degrees)

class Point():
	"""
		Class implementing support for point operations in three
		dimensional world coordinates 
	"""

	def __init__(self,x,y,z):
		self.x, self.y, self.z = x,y,z

	def copy(self):
		"""
		Creates a copy of itself
		
		Returns:
			Point: object copied from self
		"""
		return Point(self.x,self.y,self.z)

	def distance(self, to):
		"""
		Calculates the distance from this point to the given one
		
		Args:
			to (Point, float): end point to calculate distance to
		
		Returns:
			float: distance to the given point
		"""
		return float(np.sqrt(
			(self.x - to.x) ** 2 +
			(self.y - to.y) ** 2 + 
			(self.z - to.z) ** 2 ))

	def move(self, by, distance):
		"""
		Translates this point by a vector and a given distance
		
		Args:
			by (str, Vector): axis name ("x", "y" or "z") or vector describing translate direction
			distance (float): value describing distance   
		
		Returns:
			Point: translated point object
		"""

		if type(by) is str:
			by = Vector.from_axis(by)

		return Point(
			self.x + distance * by.i, 
			self.y + distance * by.j, 
			self.z + distance * by.k )

	def intersects(self, plane):
		"""
		Same as **dicom3d.Plane.intersects**, verifies point intersection with a plane
		
		Args:
			plane (Plane): plane to verify intersection with
		
		Returns:
			bool: **True** if intersects plane, **False** otherwise
		"""
		return plane.intersects(self)

	def __len__(self):
		return 3

	def __getitem__(self, item):
		if item == 0: return self.x
		if item == 1: return self.y
		if item == 2: return self.z
		raise ValueError("Point class has no item '%s'" % (item))
	
	def __iter__(self):
		yield self.x
		yield self.y
		yield self.z

	def __repr__(self):
		return "x:%.2f y:%.2f z:%.2f" % (self.x,self.y,self.z)

class Vector():
	""" 
		Class responsible for providing support for vectorial
		algebra
	"""

	def __init__(self, i=0, j=0, k=0):
		self.matrix = np.array([[i],[j],[k]], dtype=np.float)

	# PROPERTIES #
	def _geti(self): return self.matrix[0,0]
	def _getj(self): return self.matrix[1,0]
	def _getk(self): return self.matrix[2,0]
	def _seti(self,v): self.matrix[0,0] = v
	def _setj(self,v): self.matrix[1,0] = v
	def _setk(self,v): self.matrix[2,0] = v

	i = property(_geti, _seti)
	"""
		Property describing the **i** component of the vector
	"""
	j = property(_getj, _setj)
	"""
		Property describing the **j** component of the vector
	"""
	k = property(_getk, _setk)
	"""
		Property describing the **k** component of the vector
	"""

	@staticmethod
	def from_numpy(array):
		"""
		Constructs a vector from a numpy array of shape (3,1)
		
		Args:
			array (numpy.array): numpy array to import data from
		
		Returns:
			Vector: resulting vector object
		"""
		assert(array.shape == (3,1))

		i,j,k = array.T[0]
		return Vector(i,j,k)

	@staticmethod
	def from_plane(plane):
		"""
		Copies the plane normal vector
		
		Args:
			plane (Plane): plane argument
		
		Returns:
			Vector: resulting vector object
		"""
		return plane.normal.copy()

	@staticmethod
	def from_coords(origin, target):
		"""
		Constructs a vector from two points in space
		
		Args:
			origin (Point, tuple): origin or source point
			target (Point, tuple): target or end point
		
		Returns:
			Vector: resulting vector object
		"""
		xo,yo,zo = origin
		xt,yt,zt = target
		return Vector(xt-xo, yt-yo, zt-zo)

	@staticmethod
	def from_axis(axis):
		"""
		Constructs a vector from a given Axis definition
		
		Args:
			axis (str): axis name ("x", "y" or "z")
		
		Raises:
			ValueError: when an invalid axis name is passed

		Returns:
			Vector: resulting vector
		"""
		if len(axis) != 1:
			raise ValueError("invalid axes")

		axis = axis.lower()

		if axis == "z":
			return Vector.from_coords( (0,0,0), (0,0,1) )
		if axis == "y":
			return Vector.from_coords( (0,0,0), (0,1,0) )			
		if axis == "x":
			return Vector.from_coords( (0,0,0), (1,0,0) )

		raise ValueError("invalid axes")

	def copy(self):
		"""
		Creates a copy of itself
		
		Returns:
			Vector: resulting vector object
		"""
		return Vector(*self.tuple())

	def equals(self, v):
		"""
		Verifies if a vector is identical with the given one
		
		Args:
			v (Vector): vector to verify equality with
		
		Returns:
			bool: **True** if equal, **False** otherwise
		"""
		return self.tuple() == v.tuple()

	def round(self, digits=5):
		"""
		Rounds the values of **i**, **j** and **k** with a given precision
		
		Args:
			digits (int, optional): number of digits to round to, defaults to 5.
		
		Returns:
			Vector: resulting vector object
		"""
		return Vector(
			round(self.i, digits), 
			round(self.j, digits),
			round(self.k, digits))

	def numpy(self):
		"""
		Returns the corresponding numpy array for this vector
		
		Returns:
			numpy.array: corresponding numpy array
		"""
		return self.matrix

	def dot(self,v):
		"""
		Calculates the dot product of a vector with a given one
		
		Args:
			v (Vector): dot product argument
		
		Returns:
			Vector: resulting vector object
		"""
		return self.matrix.T.dot(v.matrix)[0,0]

	def mul(self,v):
		"""
		Multiplies a vector with a scalar value
		
		Args:
			v (float, int): scalar value to multiply by
		
		Returns:
			Vector: resulting vector object
		"""
		return Vector(self.i * v, self.j * v, self.k * v)

	def div(self,v):
		"""
		Divides a vector by a scalar value
		
		Args:
			v (float, int): scalar value to divide by
		
		Returns:
			Vector: resulting vector object
		"""
		return Vector(self.i / v, self.j / v, self.k / v)

	def norm(self):
		"""
		Calculates the length of the vector
		
		Returns:
			float: length of vector
		"""
		return norm(self.matrix)

	def unit(self):
		"""
		Returns the unit vector corresponding to this vector
		
		Returns:
			Vector: resulting vector object
		"""
		return Vector.from_numpy(self.matrix / norm(self.matrix))

	def invert(self):
		"""
		Returns a vector pointing in the opposite direction
		
		Returns:
			Vector: resulting vector object
		"""
		return Vector(-self.i, -self.j, -self.k)

	def tuple(self):
		""" convers a vector to a tuple """
		return (self.matrix[0][0], self.matrix[1][0], self.matrix[2][0])

	def angle(self, vector):
		"""
		Calculates the angle in radians, between this vector and the 
		one passed as argument
		
		Args:
			vector (Vector): argument vector
		
		Returns:
			float: angle measured in radians
		"""
		i,j,k = vector.tuple()
		x,y,z = self.tuple()

		n1n2 = abs(x*i + y*j + z*k)
		n1   = np.sqrt(x ** 2 + y ** 2 + z ** 2)
		n2   = np.sqrt(i ** 2 + j ** 2 + k ** 2)

		return np.arccos(n1n2 / (n1 * n2))

	def rotate_by_vector(self, vector, angle):
		"""
		Construct a vector that represents the current one rotated around a 
		given vector
		
		Args:
			vector (Vector): pivot vector to perform rotation about
			angle (float): angle measured in radians
		
		Returns:
			Vector: rotated vector object
		"""

		cos = np.cos(angle)
		sin = np.sin(angle)

		ux,uy,uz = vector.unit()
		u2x,u2y,u2z = ux * ux, uy * uy, uz * uz

		rotation = np.array([
				[ 
					cos + u2x * (1-cos)           , 
				  	ux  *  uy * (1-cos) - uz * sin, 
				  	ux  *  uz * (1-cos) + uy * sin
				],
				[   
					uy * ux * (1-cos) + uz * sin   , 
					cos + u2y * (1-cos)            , 
					uy  *  uz * (1-cos) - ux * sin 
				],
				[   
					uz * ux * (1-cos) - uy * sin, 
					uz  *  uy * (1-cos) + ux * sin , 
					cos + u2z * (1-cos) 
				]
			])

		return vector.from_numpy(self.matrix.T.dot(rotation).T)

	def rotate_by_axis(self, axis, angle):
		"""
		Construct a vector that represents the current one rotated about
		a given axis 
		
		Args:
			axis (str): axis name definition ("x", "y" or "z")
			angle (float): angle measured in radians
		
		Raises:
			ValueError: if an invalid axis name is passed
		
		Returns:
			Vector: rotated vector object
		"""
		cos = np.cos(angle)
		sin = np.sin(angle)

		# get rotation matrix
		axis = axis.lower()
		if axis == "z":
			rotation = np.array([
					[ cos, -sin, 0 ],
					[ sin,  cos, 0 ],
					[   0,    0, 1 ]
				])
		elif axis == "y":
			rotation = np.array([
					[ cos, 0, sin ],
					[   0, 1,   0 ],
					[-sin, 0, cos ]
				])
		elif axis == "x":
			rotation = np.array([
					[ 1,   0,    0 ],
					[ 0, cos, -sin ],
					[ 0, sin,  cos ]
				])
		else:
			raise ValueError("invalid axis given '%s'" % (axis))

		return Vector.from_numpy(rotation.dot(self.matrix))

	def rotate(self, by, angle):
		"""
		Wrapper function to construct rotated vectors, transparently using
		**dicom3d.Vector.rotate_by_axis** or **dicom3d.Vector.rotate_by_vector**,
		depending on the arguments given.
		
		Args:
			by (str, Vector): axis definition ("x", "y" or "z") or vector object 
			angle (float): angle measured in radians
		
		Raises:
			ValueError: if an invalid axis name is passed as argument
		
		Returns:
			Vector: rotated vector object
		"""

		if type(by) is str:
			return self.rotate_by_axis(by, angle)

		if type(by) is Vector:
			return self.rotate_by_vector(by, angle) 

		raise ValueError("invalid vector rotation arguments")

	def __len__(self):
		return 3

	def __getitem__(self, item):
		return self.matrix[item,0]

	def __iter__(self):
		for i in self.matrix.T[0]:
			yield i

	def __repr__(self):
		i,j,k = self.tuple()
		return "i:%.2f j:%.2f k:%.2f" % (i,j,k)


class Plane():
	"""
		This class provides support for the mathematical operations
		required to construct and manipulate planes
	"""
	def __init__(self, a=0, b=0, c=0, d=0):
		self.normal = Vector(a,b,c)
		self.d = d

	# PROPERTIES #
	def _geta(self): return self.normal.i
	def _getb(self): return self.normal.j
	def _getc(self): return self.normal.k
	def _seta(self,v): self.normal.i = v
	def _setb(self,v): self.normal.j = v
	def _setc(self,v): self.normal.k = v

	a = property(_geta, _seta)
	"""
	For a plane described by equation 'ax + by + cx = d', this property 
	modifies the 'a' component of the plane
	"""
	b = property(_getb, _setb)
	"""
	For a plane described by equation 'ax + by + cx = d', this property 
	modifies the 'b' component of the plane
	"""
	c = property(_getc, _setc)
	"""
	For a plane described by equation 'ax + by + cx = d', this property 
	modifies the 'c' component of the plane
	"""

	@staticmethod
	def from_coords(origin, target):
		"""
		Constructs a plane from a vector described by two points in space
		
		Note:
			The resulted plane's normal vector will be trimmed to be a unit
			vector

		Args:
			origin (tuple, Point): source or origin point 
			target (tuple, Point): target or end point
		
		Returns:
			Plane: resulting plane object

		Examples:
			>>> plane1 = Plane.from_axes("xz")
			>>> plane2 = Plane.from_coords((0,0,0),(0,1,0))
			>>> plane1.equals(plane2)
			True
		"""
		xo,yo,zo = origin
		xt,yt,zt = target

		n = Vector(xt-xo, yt-yo, zt-zo).unit()
		return Plane.from_normal(n, n.i*xo + n.j*yo + n.k*zo)

	@staticmethod
	def from_normal(normal, d=0):
		"""
		Constructs a plane from a normal vector and the **d** component.
		
		Args:
			normal (Vector): normal vector
			d (int, optional): **d** component of the plane, defaults to 0.
		
		Returns:
			Plane: resulting plane object
		"""
		return Plane(*normal.tuple(), d)

	@staticmethod
	def from_axes(axes):
		"""
		Constructs a vector from two axis
		
		Args:
			axes (str): string defining the two axis ("xy","xz" or "yz")
		
		Raises:
			ValueError: on invalid axis definition
		
		Returns:
			Plane: resulting plane object

		Examples:
			>>> oxy = Plane.from_axes("xy")
			>>> oxz = Plane.from_axes("xz")
			>>> oyz = Plane.from_axes("yz")
			>>> degrees(oxz.angle(oxy))
			90.0
		"""
		if len(axes) != 2:
			raise ValueError("too many axes")

		if "x" in axes and "y" in axes:
			return Plane.from_normal(Vector.from_axis("z"),0)
		if "x" in axes and "z" in axes:
			return Plane.from_normal(Vector.from_axis("y"),0)	
		if "y" in axes and "z" in axes:
			return Plane.from_normal(Vector.from_axis("x"),0)

		raise ValueError("invalid axes")

	def copy(self):
		"""
		Creates a copy of itself

		Returns:
			Plane: resulting plane object
		"""	
		return Plane.from_normal(self.normal, self.d)

	def equals(self, p):
		"""
		Checks if a plane is equal to another
		
		Args:
			p (Plane): argument plane to check equality
		
		Returns:
			bool: **True** if equation is equal or **False** otherwise

		Examples:
			>>> plane1 = Plane.from_axes("xy")
			>>> plane2 = Plane.from_coords((0,0,0), (0,0,1))
			>>> plane2.equals(plane1)
			True
			>>> plane2.equals(plane1.move((0,0,1)))
			False
		"""
		return self.d == p.d and self.normal.equals(p.normal)

	def round(self, digits=5):
		"""
		Rounds the **a**, **b**, **c** and **d** components of the plane
		and returns the resulting plane object
		
		Args:
			digits (int, optional): number of digits to round to, defaults to 5
		
		Returns:
			Plane: resulting plane object
		"""
		return Plane.from_normal(
			self.normal.round(digits), round(self.d, digits))

	def rotate(self, by, angle):
		"""
		Returns a plane from the current one, with the normal vector 
		rotated about an axis or another vector, by a given angle.
		
		Args:
			by (str,Vector): axis definition ("x","y" or "z") or vector object 
			angle (float): angle measured in radians
		
		Returns:
			Plane: resulting plane object
		"""
		p = Plane(*self.normal.tuple(),self.d)
		p.normal = p.normal.rotate(by, angle)
		return p

	def move(self, point):
		"""
		Returns a plane from the current one, translated to a given point
		
		Note: 
			This function will modify only the **d** component of the plane

		Args:
			point (tuple, Point): point to translate plane to 
		
		Returns:
			Plane: resulting plane object
		"""
		x,y,z = point
		a,b,c = self.normal.tuple()
		d = a*x + b*y + c*z
		return Plane(a, b, c, d)

	def parallel(self, p, tolerance = 1.e-4):
		"""
		Checks if this plane is parallel to a given one within a given range
		of tolerance
		
		Args:
			p (Plane): plane argument to check parallelism
			tolerance (float, optional): tolerance value, defaults to 1.e-4
		
		Returns:
			bool: **True** if parallel or **False** otherwise

		Examples:
			>>> plane1 = Plnae.from_axes("xy") # OXY plane
			>>> plane2 = plane1.move((0,0,10)) # move plane to this point
			>>> plane1
			0.00X + 0.00Y + 1.00Z = 0.00
			>>> plane2
			0.00X + 0.00Y + 1.00Z = 10.00
			>>> plane1.parallel(plane2)
			True
		"""
		return self.angle(p) < tolerance

	def resolve(self, point):
		"""
		Resolves the X,Y or Z component of the given point based on
		current plane equation
		
		Args:
			point (tuple, Point): point to resolve
		
		Returns:
			Point: resulting Point

		Examples:
			To find the Z component of a point that lies on the plane
			and has only the X and Y components defined:

			>>> plane = Plane.from_axes("xy").rotate("y",radians(30))
			>>> _,_,z = plane.resolve((10,10,None))
			>>> print("Resolved point is X:10 Y:10 Z:%.2f" % (z))
			Resolved point is X:10 Y:10 Z:-5.77
		"""
		x,y,z = point
		a,b,c = self.normal.tuple()
		
		# x = (d - cz - by)/a
		# y = (d - cz - ax)/b
		# z = (d - by - ax)/c

		# resolve for X
		if x is None:
			if a == 0: return point			
			x = (self.d - c * z - b * y)/a
		elif y is None:
			if b == 0: return point
			y = (self.d - c * z - a * x)/b
		elif z is None:
			if c == 0: return point
			z = (self.d - b * y - a * x)/c

		return Point(x,y,z)

	def angle(self, p):
		"""
		Calculates the angle made by the given plane with another one
		
		Args:
			p (Plane): plane argument to calculate angle with
		
		Returns:
			float: resulted angle in radians

		Note: 
			This function actually calculates the angle made by the two
			plane's normal vectors
		"""
		return self.normal.angle(p.normal)

	def intersects(self, point):
		"""
		Verifies if a given point intersects the current plane
		
		Args:
			point (tuple, Point): point argument to check intersection with
		
		Returns:
			bool: **True** if intersects plane or **False** otherwise
		"""
		x,y,z = point
		a,b,c = self.normal
		v = a*x + b*y + c*z
		return v == self.d

	def __iter__(self):
		l = [*self.normal, self.d]
		for i in l: yield i

	def __repr__(self):
		""" prints plane equation"""
		a,b,c = self.normal
		return "%.2fX + %.2fY + %.2fZ = %.2f" % (
			a, b, c, self.d)
#
# cartesian mapping utility class
#
class LocalCoordinateSystem():

	"""
		Class responsible for transforming local coordinates in a cartesian space
		to world three dimensional coordinations. A *Local Coordinate System* is
		defined by two axis vectors (one describing the X axis, the other one the Y
		axis in the cartesian bi-dimensional space) and an origin for the (0,0)
		point.

		The scaling factor is optional, but useful when the world you are mapping
		to has a different density than the local cartesian system you are using.
	"""

	def __init__(self, origin, x_vector, y_vector, scaling=(1,1)):
		""" construct a local coordinate system from X,Y vectors, origin
			and a scaling factor """

		# unwrap tuples into numpy array
		self.origin   = Point(*origin)
		self.x_vector = x_vector.copy()
		self.y_vector = y_vector.copy()
		self.scaling  = scaling

		self.update()

	def copy(self):
		"""
		Creates a copy of itself
		
		Returns:
			LocalCoordinateSystem: resulting coordinate system
		"""
		return LocalCoordinateSystem(
			self.origin, 
			self.x_vector, self.y_vector, 
			self.scaling )

	def update(self):
		"""
		For each direct modification made to this coordinate system, a call 
		to this function is required to update the transformation matrix 

		Examples:
			Assuming you decide to set a new origin point:

			>>> lcs = LocalCoordinateSystem(
					Vector.from_axis("x), 
					Vector.from_axis("y"), 
					Point(0,0,0))
			>>> lcs.origin = Point(10,10,0)
			>>> lcs.update()
			>>> # now you can safely transform from and to cartesian space
			>>> pt = lcs.to_world(0,0)
			>>> print("Origin:", pt)
		"""
		# unwrap into discreete numbers
		sx, sy, sz = self.origin
		xx, xy, xz = self.x_vector.tuple()
		yx, yy, yz = self.y_vector.tuple()
		pi, pj     = self.scaling

		# transformation matrix
		self.matrix = np.array([
				[xx * pi, yx * pj, 0, sx],
				[xy * pi, yy * pj, 0, sy],
				[xz * pi, yz * pj, 0, sz],
				[      0,       0, 0,  1]
			])


	def to_local(self, coords):
		"""
		Transforms the givel world three dimensional coordinates to local 
		cartesian coordinates
		
		Args:
			coords (Point, tuple): world three dimensional coordinates
		
		Returns:
			tuple: tuple of the resulting cartesian coordinates in **float** 
		"""

		coords = np.array([*coords])
		origin = np.array([*self.origin])

		# substract origin -> translate
		coords = coords - origin
		dx, dy = self.scaling

		# rotate
		x = coords.dot(self.x_vector.matrix)
		y = coords.dot(self.y_vector.matrix)

		x, y = x[0]/dx, y[0]/dy
		return (x,y)

	def to_world(self, x, y):
		"""
		Transform local cartesian coordinates (**x** and **y**) to three 
		dimesnional world coordinates
		
		Args:
			x (float, int): value of cartesian **x** coordinate
			y (float, int): value of cartesian **y** coordinate
		
		Returns:
			Point: point object describing resulting coordinates

		Examples:
			>>> transform = section.transfrom
			>>> transform.to_world(0,0)
			x:-73.91 y:-81.20 z:6.64
			>>> transform.to_world(10,10)
			x:-70.78 y:-78.08 z:6.6
			>>> dist = transform.to_world(10,10).distance( transform.to_world(0,0) )
			>>> print("From (0,0) to (10,10) distance is: %.1f mm" % (dist))
			From (0,0) to (10,10) distance is: 4.4 mm
		"""

		# multiply with transformation matrix
		imatrix = np.array([ [x], [y], [0], [1] ])
		rmatrix = self.matrix.dot(imatrix)

		# extract response		
		x,y,z,_ = rmatrix.T[0]
		return Point(x,y,z)

	def measure(self, point_from, point_to):

		"""
		Measures the distance from **point_from** to **point_to** in world coordinates 
		or local coordinates. 
		
		When measuring for local cartesian coordinates the result will be the distance 
		from the coresponding transformed world coordindates and viceversa. When 
		measuring distance for world coordinates, the result will be the distance
		in local coordinates.
		
		Raises:
			ValueError: inconsistent dimensions given (e.g. 2D point paired with 3D point)
			ValueError: invalid input (e.g. not a 2D point nor 3D point)
		
		Returns:
			float: measured distance in local or world coordinates 

		Examples:
			>>> # asuming we have a *dicom3d.Dataset* object
			>>> pt1, pt2 = dataset.to_mm(0,0), dataset.to_mm(10,10)
			>>> # this will measure the distance in mm between the two points
			>>> pt1.distance(pt2)
			4.419417382415922
			>>> # which is ecquivalent with this short form
			>>> dataset.transform.measure((0,0),(10,10))
			4.419417382415922
			>>> # for measuring the opposite, distance in pixels
			>>> # for the segment defined by the two points
			>>> dataset.transform.measure(pt1,pt2)
			14.142135623730951
			>>> # which is equivalent to how we calculate the diagonal
			>>> # if we knew the corresponding local points 
			>>> np.sqrt(10**2 + 10**2)
			14.142135623730951
		"""

		if len(point_from) != len(point_to):
			raise ValueError("inconsistent dimensions for measuring distance (%s,%s)" % (
				point_from, point_to))

		# points are in local space => measure world distance
		if len(point_from) == 2:
			xs, ys = point_from
			xe, ye = point_to
			pts = self.to_world(xs,ys)
			pte = self.to_world(xe,ye)
			return pts.distance(pte)

		# points are in world space => measure local distance
		if len(point_from) == 3:
			xs, ys = self.to_local(point_from)
			xe, ye = self.to_local(point_to)
			dx, dy = (xe-xs),(ye-ys)
			return np.sqrt(dx ** 2 + dy ** 2)

		raise ValueError("invalid input for measuring distance (%s,%s)" % (
			point_from, point_to))
		

	def rotate(self, by, angle):
		"""
		Rotates this coordinate system X and Y axes about a vector or an axis 
		and returns the newly modified coordinate system
		
		Args:
			by (str, Vector): axis definition ("x", "y" or "z") or vector object 
			angle (float): angle measured in radians

		Returns:
			LocalCoordinateSystem: the rotated coordinate system

		Examples:
			>>> section.transform.x_vector
			i:1.00 j:0.00 k:0.00
			>>> section.transform.rotate("z",radians(45)).x_vector
			i:0.71 j:0.71 k:0.00

		"""
		lcs = self.copy()

		# rotate LCS and update
		lcs.x_vector = self.x_vector.rotate(by, angle)
		lcs.y_vector = self.y_vector.rotate(by, angle)
		lcs.update()

		return lcs

	def move(self, by, distance):
		"""
		Translate this local coordinate system's origin by moving it
		along a given vector and by a given distance
		
		Args:
			by (str, Vector): axis name ("x", "y" or "z") or vector object describing direction of translation 
			distance (float): value describing distance
		
		Returns:
			LocalCoordinateSystem: the translated coordinate system

		Examples:
			>>> section.transform.origin
			x:-73.91 y:-81.20 z:6.64
			>>> # move on the x axis 10 mm
			>>> section.tranform.move("x", 10.0).origin
			x:-63.91 y:-81.20 z:6.64
			>>> # move on XY diagonal
			>>> vector = Vector.from_axis("x").rotate("z", radians(45))
			>>> section.transform.move(vector, 10.0).origin
			x:-66.84 y:-74.13 z:6.64
		"""
		lcs = self.copy()

		# move origin and update
		lcs.origin = lcs.origin.move(by, distance)
		lcs.update()

		return lcs

	def scale(self, by):
		"""
		Modify the scaling factor of the current coordinate system and construct
		another one with the resulting scaling factor
		
		Args:
			by (float, tuple): value or tuple of values describing the scaling factor
		
		Returns:
			LocalCoordinateSystem: the scaled coordinate system

		Examples:
			>>> transform1 = section.transform.copy()
			>>> transform2 = transform.scale(1/2)
			>>> dist1 = transform1.to_world(0,0).distance(transform1.to_world(10,10))
			>>> dist2 = transform2.to_world(0,0).distance(transform2.to_world(10,10))
			>>> print("Distance before scale: %.1f after: %.1f" % (dist1, dist2))
			Distance before scale: 4.4 after: 2.2
		"""
		lcs = self.copy()
		dx,dy = lcs.scaling

		# if factor is tuple
		if type(by) is tuple:
			by_x, by_y = by
			lcs.scaling = float(dx * by_x), float(dy * by_y)
		# if factor is float or integer
		else:
			lcs.scaling = float(dx * by), float(dy * by)
		
		lcs.update()
		return lcs