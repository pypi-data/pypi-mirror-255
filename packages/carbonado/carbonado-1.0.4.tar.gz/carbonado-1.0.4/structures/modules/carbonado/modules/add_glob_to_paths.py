
import glob
import os


def start (
	directory = None,
	extension = None,
	relative_path = None,
	verbose = None,
	
	paths = None
):
	glob_param = directory + "/**/*" + extension;
	if (verbose >= 2):
		print ("glob:", glob_param)

	finds = glob.glob (glob_param, recursive = True)
	if (verbose >= 2):
		print ("finds:", json.dumps (finds, indent = 4))
	
	for find in finds:
		path = os.path.relpath (find, relative_path)
		name = path.split (extension) [0]
	
		paths.append ({
			"path": path,
			"name": name,
			"find": find
		})