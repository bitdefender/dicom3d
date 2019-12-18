#! /usr/bin/env python3
import os
import dicom3d as d3d
from   dicom3d.plotter import plotter

import pydicom
from pydicom.data import get_testdata_files

intro = """
===-----------------------------------------------------===
 |                   PLANAR SECTIONS                     |
===-----------------------------------------------------===

    This example shows how to create sections from a 
    planar dataset and not a volumetric scan.

    It uses the 'Section.from_dataset()' function to 
    construct a section from a single dataset. The
	dataset is obtained from 'pydicom' sample files.

    The Section's transform properties can then be used
	to rotate, scale and translate the section image.
    
    Each section image is plotted using matplotlib.

===-----------------------------------------------------===
"""

if __name__ == "__main__":

	print(intro)

	# loading dataset from pydicom
	files = get_testdata_files("MR_small_bigendian.dcm")
	print("Loading dataset from: ", files[0])
	dataset = pydicom.dcmread(files[0])

	# construct a section from planar dataset
	planar_section = d3d.Section.from_dataset(dataset)

	# get wrapped dicom3d.Dataset class
	dataset = planar_section.series.first()
	origin = dataset.center()

	# navigate through dataset
	topleft = dataset.to_mm(0,0)
	print("Pixel at (0,0) is at %s" % (topleft))

	topright = dataset.to_mm(dataset.Columns,0)
	print("Pixel at (%d,%d) is at %s" % (dataset.Columns, 0, topright))

	btmleft = dataset.to_mm(0,dataset.Rows)
	print("Pixel at (%d,%d) is at %s" % (0, dataset.Rows, btmleft))

	# measure size of dataset in world coordinates
	width = topright.distance(topleft)
	height = btmleft.distance(topleft)
	print("Dataset width: %.2f mm height: %.2f mm" % (width, height))

	# decrease density by a factor of two
	dx,dy = planar_section.pixel_density
	planar_section.pixel_density = dx/2, dy/2
	img_low_density1 = planar_section.image((width,height))

	print("Creating low-density section..")

	# decrease density by a factor of two
	planar_section.pixel_density = dx/4, dy/4
	img_low_density2 = planar_section.image((width,height))

	# reset density
	planar_section.pixel_density = dx, dy

	print("Creating default section..")

	# extract an image of Columns,Rows pixels containing dataset center
	width, height = dataset.Columns, dataset.Rows 
	img_simple = planar_section.image((width,height))

	print("Creating rotated section..")

	# backup section's transformation system
	transform_backup = planar_section.transform

	# rotate section's orientation axes by 30º degrees
	planar_section.transform = \
		planar_section.transform.rotate("z", d3d.radians(30))

	# get section image
	img_rotated = planar_section.image((width,height))

	print("Creating section translated after rotation..")

	# move section's origin along a X axis by 10.0 mm
	planar_section.transform = \
		planar_section.transform.move(
			planar_section.transform.x_vector, 
			10.0)
	
	# get section image
	img_translated_rotated = planar_section.image((width,height))

	print("Creating translated section..")

	# translate again using backed-up transform system
	planar_section.transform = \
		transform_backup.move(
			transform_backup.x_vector, 
			10.0)

	# get section image
	img_translated = planar_section.image((width,height))

	print("---\nPlotting..")
	plt = plotter(figsize=(8,8), rows=2, columns=3)

	plt.subnew()
	plt.image(img_low_density1, title="50% density")

	plt.subnew()
	plt.image(img_low_density2, title="25% density")

	plt.subnew()
	plt.image(img_simple, title="100% density")

	plt.subnew()
	plt.image(img_rotated, title="rotated")

	plt.subnew()
	plt.image(img_translated_rotated, title="translated after rotation")

	plt.subnew()
	plt.image(img_translated, title="translated")

	plt.show()
