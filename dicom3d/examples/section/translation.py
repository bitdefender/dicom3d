#! /usr/bin/env python3
import os
import dicom3d as d3d
from   dicom3d.data import select_file
from   dicom3d.plotter import plotter

intro = """
===-----------------------------------------------------===
 |                TRANSLATED SECTIONS                    |
===-----------------------------------------------------===

    This example shows how to create translated sections
    from a volumetric scan.

    It creates a set of 9 section of 128x128 pixels, each 
    translated across the sagital plane (OYZ) by the same
    offset, 128 pixels horizontally and 128 pixels 
    vertically.

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

    image_size = (128,128)
    pixel_offsets = [
        (-128,-128), (0, -128), (128,-128),
        (-128,   0), (0,    0), (128,   0),
        (-128, 128), (0,  128), (128, 128)
    ]

    # reference section
    # this section will share the same plane with all translated
    # sections, will differ only in origin (center)
    reference_section = d3d.Section.from_plane(series, plane_org.move(origin), origin)
    transform = reference_section.transform

    # calculate translations using the reference section above
    # and transform offsets from pixel offsets to world coordinates
    coordinate_offsets = [
        transform.to_world(dx,dy) for dx,dy in pixel_offsets
    ]

    for idx, target in enumerate(coordinate_offsets):

        tx,ty,tz = target
        dx,dy = pixel_offsets[idx]

        print("\nTranslating section to"
                "\n=> X: %.2fmm Y:%.2fmm Z:%.2fmm"
                "\n=> By: %d, %d pixels" % (
                    tx, ty, tz, dx, dy))

        # move OYZ plane to targeted section center
        plane = plane_org.move(target)
        print("=>", plane)

        try:
            section = d3d.Section.from_plane(series, plane, target)
            image = section.image(image_size)
            plt.subnew()
            plt.image(image, title="%d,%d" % (dx, dy))
        except Exception as e:
            print("Exception for section with translation %d,%d (%s)" % (
                dx,dy, e))
            continue

    plt.show()
