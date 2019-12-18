#! /usr/bin/env python3
import os
import dicom3d as d3d
from   dicom3d.data import select_file
from   dicom3d.plotter import plotter
import numpy as np
import imageio

intro = """
===-----------------------------------------------------===
 |                MAKING A .GIF ANIMATION                |
===-----------------------------------------------------===

    This example shows how to create an animated GIF out
    of dicom3d's reconstructed sections. It needs a 
    volumetric scan to build sections from.

    This example will first list the planes and origins
    for each sections to be constructed and then it will
    create an animated .GIF file using 'imageio' library.
    
    The resulted animation will be saved to a file named
    'rotated.gif' in the current directory.

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

def construct_sectioning_path():
    global series

    # get mid-dataset and its center
    middle = series.middle()
    center = middle.center()
    plane = d3d.Plane.from_axes("xz")

    x1,y,z = middle.to_mm(0,0)
    x2,_,_ = middle.to_mm(middle.Columns,0)

    origin = d3d.Point((x2-x1)/2 + x1, y, z)

    path = []

    step_cnt  = 30
    step_size = (center.y - origin.y)/step_cnt

    # advance to center by y
    for i in range(0,step_cnt):
        path.append((origin, plane))
        origin = origin.copy()
        origin.y += step_size
    
    # rotate plane 
    step_cnt = 45
    step_size = 90.0/step_cnt

    for i in range(0, step_cnt):
        plane = plane.rotate("z", d3d.radians(step_size))
        path.append((origin, plane))

    # translate to right
    step_cnt = 30
    step_size = (x2-origin.x)/step_cnt

    for i in range(0, step_cnt):
        origin = origin.copy()
        origin.x += step_size
        path.append((origin, plane))

    return path

if __name__ == "__main__":

    print(intro)

    # loading DICOMDIR path
    series_path = select_series_path()
    print("Loading series from: ", series_path)

    series = d3d.Series.from_directory(series_path, "*.dcm")
    middle = series.middle()

    dataset_width, dataset_height = (
        middle.transform.measure((0,0),(middle.Columns,0)),
        middle.transform.measure((0,0),(0,middle.Rows))
    )

    # calculate section size
    image_size = (dataset_width/2,dataset_height/2)

    print("---")
    print("Pixel spacing        : %.2f, %.2f mm" % (middle.PixelSpacing[0], middle.PixelSpacing[1]))
    print("Thickness            : %.2f mm" % ( middle.SliceThickness ))
    print("Dataset size         : %.1f x %.1f mm" % (dataset_width, dataset_height ))
    print("Section size         : %.1f x %.1f mm" % (image_size[1], image_size[0] ))
    print("---")

    # create path for this animation
    path = construct_sectioning_path()

    oxz = d3d.Plane.from_axes("xz")
    # create images
    images = []
    for origin, plane in path:
        
        plane = plane.move(origin)
        angle = plane.angle(oxz)
        print("Section origin: %s Rotation Angle: %.2f" % (
            origin, d3d.degrees(angle) ))

        try:
            section = d3d.Section.from_plane(series, plane, origin)
            image = section.image(image_size)
            images.append(image)
        except Exception as e:
            print("Exception for section (%s)" % (e))
            pass

    imageio.mimsave('./rotate.gif', images)
