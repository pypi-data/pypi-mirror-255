
'''
	python3 status.proc.py "_status/checks/1/status_1.py"
'''

import carbonado

import time

def check_1 ():
	import pathlib
	this_directory = pathlib.Path (__file__).parent.resolve ()

	from os.path import dirname, join, normpath
	structures = normpath (join (this_directory, "carbonado"))
	
	the_carbonado = carbonado.start ()
	port = the_carbonado.port;
	
	import requests
	r = requests.get (f'http://localhost:{ port }')
	assert (r.status_code == 200)

	time.sleep (2)
	
	the_carbonado.stop ()

	return;
	
	
checks = {
	"check 1": check_1
}