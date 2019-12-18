from os.path import abspath, join, dirname
from os import walk
import fnmatch

# for future use
# currently set to the current working directory
DATA_ROOT = abspath('.')

def walk_data(base, pattern, search_files=True, search_dirs=False):
	""" Enuerates the files in data directory """

	# if the user forgot to add them
	pattern = "*" + pattern + "*"

	files = []
	for root, dirnames, filenames in walk(base):

		# filter only directories
		if search_dirs:
			for directory in dirnames:
				dirname_filter = fnmatch.filter([join(root, directory)],
												 pattern)
				if len(dirname_filter):
					files.append(dirname_filter[0])

		# filter only files
		if search_files:

			for filename in filenames:
				filename_filter = fnmatch.filter([join(root, filename)],
												 pattern)
				if len(filename_filter):
					files.append(filename_filter[0])

	return files

def select_file(base_dir, pattern, 
				search_files, search_dirs, 
				selection_name, truncate_abspath=True):

	"""
	Enumerates all files and folders starting from *base_dir* and 
	prints to the console file options matching given *pattern*,
	waiting for the user to interactively select a file.

	If the user aborted the process, the function will run **exit** to
	abort the program.
	
	Args:
		base_dir (str): base directory to start search from
		pattern (str): wildcard pattern to select files or folders (e.g. *.dcm)
		search_files (bool): True to add files to the resulted list
		search_dirs (bool): True to add directories to the resulted list
		truncate_abspath (bool, optional): option to truncate **base_dir** from the printed paths

	Returns:
		str: the path to the selected file
	"""
	
	# enumerate test data directories, to lookup for series of DICOM files
	selected_files = walk_data(
		base_dir, pattern, 
		search_files=search_files, search_dirs=search_dirs )

	# make all paths relative
	if truncate_abspath:
		selected_files = [ 
			fullpath[len(base_dir)+1:] 
				for fullpath in selected_files 
					if "__" not in fullpath ]

	# empty selection?!
	if len(selected_files) == 0:
		print("No '%s' found in '%s'" % (pattern, base_dir))
		exit(-1)

	for idx, file in enumerate(selected_files):
		print("[%2d] - %s" % (idx+1, file))

	# users can select what series to process
	try:
		while True:
			selection = input("Select %s [1-%d]: " % (
				selection_name, len(selected_files)) )

			selection = int(selection)
			if selection > len(selected_files) or selection < 1:
				print("Invalid selection: %s" % selection)
				continue
			break
			
		selection_path = selected_files[selection-1]
	except Exception as e:
		print("Exception: ", e)
		exit(-1)
	except KeyboardInterrupt:
		print("\nGood bye!")
		exit(0)

	return selection_path

def get_testdata_files(pattern="*"):
	""" Return test data files from dicom3d data root directory """

	data_path = join(DATA_ROOT, 'test_files')

	files = walk_data(
		base=data_path, pattern=pattern, 
		search_files=True, search_dirs=False)

	return [filename for filename in files if not filename.endswith('.py')]

def get_testdata_dirs(pattern="*"):
	""" Return test data folders from dicom3d data root directory """

	data_path = join(DATA_ROOT, 'test_files')

	dirs = walk_data(
		base=data_path, pattern=pattern, 
		search_files=False, search_dirs=True)

	return [dirname for dirname in dirs]