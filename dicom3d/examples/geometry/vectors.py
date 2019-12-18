#!/usr/bin/env python3
import dicom3d.geometry as g

intro = """
===-----------------------------------------------------===
 |                   VECTOR GEOMETRY                     |
===-----------------------------------------------------===

    This example shows dicom3d's mathematical support in 
    regards of how to use and manipulate vectors.

    It exemplifies how to move and rotate a vector by a 
    given axis (X,Y or Z) and around a given pivot vector.

    It also shows how to create the dot product of two
    vectors, how to multiply a vector with a scalar and
    how to create unit vectors.

===-----------------------------------------------------===
"""

def print_angles(vrot):
	""" print the angles made by a vector with X,Y and Z axis """
	print("angles -> X axis: %.2fº Y axis: %.2fº Z axis: %.2fº\n" % (
		g.degrees(g.Vector.from_axis("X").angle(vrot)),
		g.degrees(g.Vector.from_axis("Y").angle(vrot)),
		g.degrees(g.Vector.from_axis("Z").angle(vrot))
	))

def rotate_by_axis(vec, axis, identity_axis):
	""" rotate a vector around a given axis """

	print("---\nrotating %s CCW around %s axis, 90 degrees:" %(
		vec, axis.upper()) )

	vrot = vec.rotate(axis,g.radians(-90))
	print("-> ",vrot)
	print_angles(vrot)

	# use vector.round(digits) to normalize float values
	print("identical to %s axis -> %s" % (
		identity_axis.upper(),
		vrot.round(10).equals(g.Vector.from_axis(identity_axis)),
	))

	# rotate it 45 deg
	print("\nrotate %s CCW around %s axis, 45 degrees: " %(
		vec, axis.upper()) )

	vrot = vec.rotate(axis, g.radians(-45))
	print("-> ",vrot)
	print_angles(vrot)

	print("identical to %s axis -> %s" % (
		identity_axis.upper(),
		vrot.round(10).equals(g.Vector.from_axis(identity_axis)),
	))


def rotate_by_vector(axis, vec, degrees):
	""" rotate a vector around another vector """

	vrot = g.Vector.from_axis(axis)
	print("---\nrotating %s unit vector around %s, %d degrees:" % (
		axis.upper(), vec, degrees
	))

	# rotate around vector
	vrot = vrot.rotate(vec, g.radians(degrees)).round()
	print("-> ",vrot)
	print_angles(vrot)

	# bring back
	print("rotating back:")
	vrot = vrot.rotate(vec, g.radians(-degrees)).round()
	print("-> ",vrot)
	print_angles(vrot)

if __name__ == "__main__":
	print(intro)

	"""
		construct a unit vector from Z axis
		rotate the vector around X axis, 90 degrees, 
		must end up being identical to Y axis
	"""

	print("\n -- rotation - around axis --\n")
	rotate_by_axis(g.Vector.from_axis("z"), "X", "Y")

	"""
		construct a unit vector from X axis androtate 
		the vector around Z axis 45 degrees; 

		use it as a pivot vector to rate around it other
		vectors
	"""
	print("\n -- rotation - around another vector --\n")
	vec = g.Vector.from_axis("x").rotate("z",g.radians(-45))
	rotate_by_vector("X", vec, 45)
	rotate_by_vector("Y", vec, 45)

	"""
		multiply the vector with a scalar; you can use 
		vector.div() to divide by a scalar
	"""
	print(" -- multiplication - scalar --\n")
	multiply = 12.5
	vec = vec.mul(multiply)

	print("multiplying vector with %.2f\n%s (length: %.2f)" % (
		multiply, vec, vec.norm()
	))

	"""
		dot product of two vectors
	"""
	print("\n -- dot product --\n")
	print("of %s" % (vec))
	print("- with X axis unit vector: %.2f" % (vec.dot(g.Vector.from_axis("x"))))
	print("- with Y axis unit vector: %.2f" % (vec.dot(g.Vector.from_axis("y"))))
	print("- with Z axis unit vector: %.2f" % (vec.dot(g.Vector.from_axis("z"))))

	"""
		creating an unit vector from an arbitrary vector
	"""
	vec = vec.unit()
	print("\nreduced unit vector: %s" % (vec.unit()))
