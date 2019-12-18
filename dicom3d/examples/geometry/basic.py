#!/usr/bin/env python3
import dicom3d.geometry as g

intro = """
===-----------------------------------------------------===
 |                   BASIC GEOMETRY                      |
===-----------------------------------------------------===

    This example shows the basic usage of dicom3d's 
    mathematical backend.

    It shows various ways of how to create vectors and
    planes, to access and manipulate their components.

===-----------------------------------------------------===
"""

if __name__ == "__main__":
	print(intro)
	print("-- constructing a plane and vector --\n")

	# construct a basic vector describing Z axis
	z_axis = g.Vector(0,0,1)

	# alternative ways to construct the same vector
	z_axis = g.Vector.from_axis("z")
	z_axis = g.Vector.from_plane(g.Plane.from_axes("xy"))
	z_axis = g.Vector.from_coords((0,0,0),(0,0,10.0)).unit() # converst to unit vector

	# construct XY plane
	plane_xy = g.Plane(0,0,1,0)

	# alternative ways to construct the same plane
	plane_xy = g.Plane.from_axes("xy")
	plane_xy = g.Plane.from_normal(z_axis, d=0)
	plane_xy = g.Plane.from_coords((0,0,0),(0,0,10)) 

	# normal vector of xy plane and Z axis should be identical
	print("Z Vector : ", z_axis)
	print("XY Plane : ", plane_xy)
	print("XY Normal: ", plane_xy.normal)

	print("plane's normal equals vector: ", plane_xy.normal.equals(z_axis))

	# other ways to get vector coordinates
	print("\n -- ways to get vector's coordinates --\n")

	i,j,k = z_axis.tuple()
	print("z_axis.tuple() : i:%.1f j:%.1f k:%.1f" % (i, j, k))

	i,j,k = z_axis
	print("unwraping      : i:%.1f j:%.1f k:%.1f" % (i, j, k))
	print("properties     : i:%.1f j:%.1f k:%.1f" % (z_axis.i, z_axis.j, z_axis.k))

	# ways to get plane information
	print("\n -- ways to get plane's coordinates --\n")

	a,b,c,d = plane_xy
	print("unwraping     : a:%.1f b:%.1f c:%.1f d:%.1f" % (a, b, c, d))
	print("properties    : a:%.1f b:%.1f c:%.1f d:%.1f" % (
		plane_xy.a, plane_xy.b, plane_xy.c, plane_xy.d))

	# modifying properties
	print("\n -- modifying properties --\n")
	z_axis.k = 2
	plane_xy.c = 2
	plane_xy.normal.k = 2

	print("vector   : ", z_axis)
	print("plane    : ", plane_xy)


