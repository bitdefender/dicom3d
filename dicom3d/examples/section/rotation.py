#! /usr/bin/env python3
import os
import dicom3d as d3d
from   dicom3d.data import select_file
from   dicom3d.plotter import plotter

intro = """
===-----------------------------------------------------===
 |                   ROTATED SECTIONS                    |
===-----------------------------------------------------===

    This example shows how to create rotated sections
    from a volumetric scan.

    It starts from a section parallel with OYZ plane, 
    moved to the center of the volumetric scan and then 
    it uses the Z axis to rotate it 180º.
    
    It then plots each section using matplotlib.

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
    plane_org = d3d.Plane.from_axes("yz")

    # create images
    print("---\nPlotting..")
    plt = plotter(figsize=(8,8), rows=3, columns=3)

    image_size = (256,256)

    for angle in range(0,180,20):

        print("---\nRotating section plane by %d degrees" % (angle))
        plane = plane_org.rotate("z", d3d.radians(angle)).move(origin)
        print("=>", plane)

        try:
            section = d3d.Section.from_plane(series, plane, origin)
            image = section.image(image_size)

            plt.subnew()
            plt.image(image, title="%dº" % (angle))
        except Exception as e:
            print("Exception for section with angle %d (%s)" % (angle, e))
            continue

    plt.show()
