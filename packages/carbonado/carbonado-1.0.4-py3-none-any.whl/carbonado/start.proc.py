



def add_paths_to_system (paths):
	import pathlib
	field = pathlib.Path (__file__).parent.resolve ()

	from os.path import dirname, join, normpath
	import sys
	for path in paths:
		sys.path.insert (0, normpath (join (field, path)))

add_paths_to_system ([
	'../../modules',
	'../../modules_pip'
])

import pathlib
from os.path import dirname, join, normpath
this_dir = pathlib.Path (__file__).parent.resolve ()

from carbonado import clique; clique ()