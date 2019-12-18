import sys
import os
from os.path import abspath, dirname, join
from dicom3d.data import walk_data, select_file

EXAMPLES_PATH = abspath(dirname(__file__))

def select_example():
    return select_file(
		base_dir = EXAMPLES_PATH, 
		pattern = "*.py",
		search_files = True,
		search_dirs = True,
		selection_name = "example" )

if __name__ == "__main__":

	# print usage
	if len(sys.argv) > 2:
		print(
			"\n"
			"Usage: python -m dicom3d.examlples [EXAMPLE_PATH]"
			"\n"
			"   Examples:"
			"        python -m dicom3d.examples geometry/basic.py"
			"    or  python -m dicom3d.examples"
			"\n")

	# enumerate examples
	if len(sys.argv) == 1:
		example_path = select_example()

	elif len(sys.argv) == 2:
		example_path = sys.argv[1]
	
	# run example
	os.system("python3 " + join(EXAMPLES_PATH, example_path))