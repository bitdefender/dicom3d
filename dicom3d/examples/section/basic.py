#! /usr/bin/env python3
import os
import dicom3d as d3d
from   dicom3d.data import select_file
from   dicom3d.plotter import plotter

intro = """
===-----------------------------------------------------===
 |                   BASIC SECTIONS                      |
===-----------------------------------------------------===

    This example shows how to create basic sections from 
    a volumetric scan.

    It will create the sagittal, axial and coronal medical
	sections form the selected volumetric scan.

	The volumetric scan must a folder of .DCM files located
	in the current working directory.
    
    Each section image is plotted using matplotlib.

===-----------------------------------------------------===
"""

def select_series_path():
    print("Select a folder containing a list of '.dcm' files:")
    return select_file(
		base_dir = os.path.abspath('.'), 
		pattern = "*",
		search_files = False,
		search_dirs = True,
		selection_name = "series" )

if __name__ == "__main__":
	print(intro)

	# loading DICOMDIR path
	series_path = select_series_path()
	print("Loading series from: ", series_path)

	series = d3d.Series.from_directory(series_path, "*.dcm")	

	# get center of mid-dataset as origin
	origin = series.middle().center()

	# construct section planes and move them to selected origin
	plane_axial    = d3d.Plane.from_axes("xy").move(origin)
	plane_sagittal = d3d.Plane.from_axes("xz").move(origin)
	plane_coronal  = d3d.Plane.from_axes("yz").move(origin)

	# create sections for each plane
	section_axial    = d3d.Section.from_plane(series, plane_axial   , origin)
	section_sagittal = d3d.Section.from_plane(series, plane_sagittal, origin)
	section_coronal  = d3d.Section.from_plane(series, plane_coronal , origin)

	# print section info
	ox,oy,oz = origin
	print("---\nOrigin: X:%.2f Y:%.2f Z:%.2f" % (ox, oy, oz))
	print("Axial    plane: %s DPI: %.2f" % (plane_axial , section_axial.dpi[0]))
	print("Coronal  plane: %s" % (plane_coronal))
	print("Sagittal plane: %s" % (plane_sagittal))

	# create images
	image_size = (512,512)

	print("---\nCreating axial image..",end="")
	img_axial   = section_axial.image(size=image_size)
	
	print("done.\nCreating sagittal image..",end="")
	img_sagittal = section_sagittal.image(size=image_size)

	print("done.\nCreating coronal image..",end="")
	img_coronal = section_coronal.image(size=image_size)
	print("done.")

	print("---\nPlotting..")
	plt = plotter(figsize=(8,8), rows=1, columns=3)

	plt.subnew()
	plt.image(img_axial, title="axial")

	plt.subnew()
	plt.image(img_sagittal, title="sagittal")

	plt.subnew()
	plt.image(img_coronal, title="coronal")

	plt.show()
