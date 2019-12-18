#!/usr/bin/env python3
import dicom3d.geometry as g

intro = """
===-----------------------------------------------------===
 |                   PLANE GEOMETRY                      |
===-----------------------------------------------------===

    This example shows dicom3d's mathematical support in 
    regards of how to use and manipulate planes.

    It exemplifies how to move and rotate a plane by a 
    given axis (X,Y or Z) and around a given pivot vector.

===-----------------------------------------------------===
"""

def print_angles(prot):
	global oxy, oxz, oyz
	""" print the angles made by a vector with X,Y and Z axis """
	print("angles -> OXY: %.2fº OXZ: %.2fº OYZ: %.2fº\n" % (
		g.degrees(oxy.angle(prot)),
		g.degrees(oxz.angle(prot)),
		g.degrees(oyz.angle(prot))
	))

def rotate_by_axis(plane, axis, identity_plane):
	""" rotate a plane around a given axis """

	# rotate 45 degrees
	print("---\nrotating %s CW around %s axis, 90 degrees:" %(
		plane, axis.upper()) )

	prot = plane.rotate(axis, g.radians(90))
	print("->",prot)
	print_angles(prot)

	# use vector.round(digits) to normalize float values
	print("identical to %s plane -> %s" % (
		identity_plane.upper(),
		prot.round(10).equals(g.Plane.from_axes(identity_plane)),
	))

	# rotate it 45 deg
	print("\nrotate %s CW around %s axis, 45 degrees: " %(
		plane, axis.upper()) )

	prot = plane.rotate(axis, g.radians(45))
	print("-> ",prot)
	print_angles(prot)

	print("identical to %s axis -> %s" % (
		identity_plane.upper(),
		prot.round(10).equals(g.Plane.from_axes(identity_plane)),
	))

def rotate_by_vector(plane, vec, degrees):
	""" rotate a plane around a vector """

	print("---\nrotating %s around %s, %d degrees:" % (
		plane, vec, degrees
	))

	# rotate around vector
	prot = plane.rotate(vec, g.radians(degrees)).round()
	print("-> ",prot)
	print_angles(prot)

	# bring back
	print("rotating back:")
	prot = prot.rotate(vec, g.radians(-degrees)).round()
	print("-> ",prot)
	print_angles(prot)

def move_plane_to(plane, point):
	""" moving a plane to a certain given point """

	x,y,z = point
	print("---\nmoving %s to (%.2f,%.2f,%.2f):" % (
		plane, x, y, z,
	))

	print("intersects point: %s" % (plane.intersects(point)))
	print_angles(plane)

	p = plane.move(point)
	print("-> ",p,"\n")

	print("intersects point: %s" % (p.intersects(point)))
	print_angles(p)

if __name__ == "__main__":
	print(intro)
	print("plane operations\n")

	# construct standard planes
	oxy = g.Plane.from_axes("xy")
	oxz = g.Plane.from_axes("xz")
	oyz = g.Plane.from_axes("yz")

	"""
		rotate the OXY plane around Y axis, 90 degrees; 
		the plane must end up being identical to OYZ
	"""

	print("\n -- rotation - around axis --\n")
	rotate_by_axis(oxy, "Y", "yz")

	"""
		construct a vector from X axis, rotate it about Z
		45 degrees, ending the diagonal of XY axes;
		use the vector as pivot for rotating XY plane
	"""
	print("\n -- rotation - around another vector --\n")
	vec = g.Vector.from_axis("X").rotate("Z",g.radians(-45))
	rotate_by_vector(oxy, vec, 45)
	rotate_by_vector(oxz, vec, 45)

	"""
		move the OXY plane to a certain point,
		and test intersection with that point
	"""
	print("\n -- translation --\n")
	move_plane_to(oxy, (10,10,10))



