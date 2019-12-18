#! /usr/bin/env python3
import os
import dicom3d as d3d
import dicom3d.dicomdir as ddir
from   dicom3d.data import get_testdata_files, select_file

intro = """
===-----------------------------------------------------===
 |                   DICOMDIR FILES                      |
===-----------------------------------------------------===

    This example shows how to use the dicom3d support to 
    load and access data from DICOMDIR files.

    DICOMDIR is a directory file that can store multiple
    series of DICOM files, organised in studies and 
    records. Each record can store multiple studies, each
    study can hold one or more DICOM dataset files.  

    This examples shows how to list and search specific 
    records, studies and series based on their attributes.

===-----------------------------------------------------===
"""

def select_dicomdir():
    print("Select a DICOMDIR file:")
    return select_file(
		base_dir = os.path.abspath('.'), 
		pattern = "*/DICOMDIR",
		search_files = True,
		search_dirs = False,
		selection_name = "dicomdir" )

def count_images(dd):

	images = 0
	for series in dd.all_series:
		images += len(series.get("datasets"))

	return images

if __name__ == "__main__":
	print(intro)

	# fetch test data files from pydicom
	dicomdir_path = select_dicomdir()

	# helper object to manage dicomdir files
	dd = ddir.DiicomDir()

	# load the DICOMDIR file
	print("Loading DICOMDIR file..",end="")
	dd.load(dicomdir_path)
	print("done")

	print("\nDICOMDIR has %d records, %d studies, %d series with %d images!" % (
		len(dd.records), len(dd.all_studies), 
		len(dd.all_series), count_images(dd)))

	# print content
	print("---\nLoaded records are:")
	dd.print()

	# finding reccords, studies and series in a DICOMDIR
	print("---\nFinding records, studies and series in DICOMDIR")
	series_attrs = { "SeriesNumber"     : 2 }
	study_attrs  = { "StudyDescription" : "Brain-MRA" }
	record_attrs = { "PatientName"      : "Doe^Archibald"}

	records = dd.find_records(record_attrs)
	print("Found %d records with attributes %s" % (
		len(records), record_attrs))

	studies = dd.find_studies(dd.records, study_attrs)
	print("Found %d studies with attributes %s" % (
		len(studies), study_attrs))

	series = dd.find_series(dd.all_studies, series_attrs)
	print("Found %d series  with attributes %s" % (
		len(series), series_attrs))

	series = dd.find_series(studies, series_attrs)
	print(".. from which %d are from study with attributes %s" % (
		len(series), study_attrs))

	# constructing a dicom3d series from a DICOMDIR
	print("---\nConstructing a dicom3d series from DICOMDIR")
	datasets = dd.all_series[0].get("datasets")
	
	# some DICOMDIR have duplicate datasets on the Z axis
	# this experimental function attempts to fix it
	curated = d3d.Series.fix_z_duplicates(datasets) 
	if len(curated) != len(datasets):
		print("Warning: fixed duplicated datasets on the Z axis (reduced from %d to %d datasets)." % (
			len(datasets), len(curated)
		))

	try:
		# construct a dicom3d series 
		series = d3d.Series(curated)
	except BaseException as e:
		print("Exception while loading series: %s" % (e))
		exit(-1)

	# print series information
	print("\n"
		"Resulted series has %d datasets, first dataset starts at %.2f mm "
		"on the Z axis, while the last one is at %.2f mm.\n"
		"The center point of the volumetric scan is: %s" % (
			series.count(),
			series.first().ZLocation,
			series.last().ZLocation,
			series.middle().center()
		))

