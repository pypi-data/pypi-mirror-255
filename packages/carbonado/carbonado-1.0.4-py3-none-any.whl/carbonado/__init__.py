

'''
	import carbonado
	carbonado = carbonado.start ()
	
	carbonado.server.stop ()
'''

import glob
import inspect
import json
import os
import pathlib
import rich

import carbonado.basin as basin
from carbonado._clique import clique

import carbonado.climate as climate
import carbonado.modules.add_glob_to_paths as add_glob_to_paths

import law_dictionary

def retrieve_directory ():
	return os.getcwd ()
	return os.path.dirname (
		os.path.abspath ((inspect.stack () [1]) [1])
	)

	
	
def start (
	params = {},
	verbose = 1
):	
	the_climate = climate.scan ();
	preconfigured_extensions = the_climate ["preconfigured extensions"]

	if (verbose >= 1):
		print ()
		print ('"carbonado" is starting.')
		print ('The module path is:', pathlib.Path (__file__).parent.resolve ())
		print ()

	rich.print_json (data = {
		"params before parsing": params
	})

	law_dictionary.check (	
		allow_extra_fields = True,
		laws = {
			"directory": {
				"required": False,
				"contingency": retrieve_directory,
				"type": str
			},
			"relative path": {
				"required": False,
				"contingency": retrieve_directory,
				"type": str
			},
			"port": {
				"required": False,
				"contingency": 2345,
				"type": int
			},
			"static port": {
				"required": False,
				"contingency": False,
				"type": bool 
			},
			"verbose": {
				"required": False,
				"contingency": 1,
				"type": int
			},
			"extensions": {
				"required": False,
				"contingency": preconfigured_extensions,
				"type": list
			}
		},
		dictionary = params
	)
	
	extensions = params ["extensions"]
	directory = params ["directory"]
	relative_path = params ["relative path"]
	static_port = params ["static port"]
	start_at_port = params ["port"]

	name_of_label = os.path.basename (directory)

	rich.print_json (data = {
		"params after parsing": params
	})


	paths = []
	for extension in extensions:
		add_glob_to_paths.start (
			directory = directory,
			extension = extension,
			relative_path = relative_path,
			verbose = verbose,
			
			paths = paths
		)
	
	
	if (verbose >= 1):
		print ("paths:", json.dumps (paths, indent = 4))
	
	the_server = basin.start (
		paths = paths,
		name_of_label = name_of_label,
		
		start_at_port = start_at_port,
		static_port = static_port
	)
	
	server = the_server ["server"]
	actual_port = the_server ["port"]
	
	server.start ()
	
	def stop ():
		if (verbose >= 1):
			print ('"carbonado" is stopping.')
	
		
		#server.stop ()
		termination = server.terminate ()
		#server.join ()
	
		if (verbose >= 1):
			print ('"carbonado" has stopped.')
			print ()
	
	import atexit
	atexit.register (stop)
	
	print ('The carbonado server has started')

	class Proceeds ():
		def __init__ (this, server, stop, port):
			this.stop = stop;
			this.port = port;
			

	return Proceeds (
		server,
		stop,
		actual_port
	)