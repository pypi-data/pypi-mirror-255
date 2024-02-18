

'''
	https://stackoverflow.com/questions/15562446/how-to-stop-flask-application-without-using-ctrl-c
'''

#
#	https://stackoverflow.com/questions/2470971/fast-way-to-test-if-a-port-is-in-use-using-python
#
def is_port_in_use (port: int) -> bool:
	import socket
	with socket.socket (socket.AF_INET, socket.SOCK_STREAM) as s:
		return s.connect_ex (('localhost', port)) == 0

import flask
from flask import Flask
from multiprocessing import Process
import pathlib
from os.path import dirname, join, normpath
THIS_FOLDER = pathlib.Path (__file__).parent.resolve ()

import carbonado.basin.treasury as treasury

def start (
	paths = [],
	name_of_label = "",
	
	start_at_port = 2345,
	static_port = False
):
	app = Flask (__name__)

	treasury_string = treasury.start (
		links = paths,
		name_of_label = name_of_label
	)

	@app.route ("/")
	def treasury_route ():
		return treasury_string
	
	@app.route ("/<path:path>")
	def page (path):
		#print (path)
		
		try:
			for found_path in paths:
				if (found_path ['path'] == path):
					the_extension = pathlib.Path (path).suffix
					
					if (the_extension in [ ".jpg", ".png" ]):
						f = open (found_path ['find'], mode = "rb")
						data = f.read ()
						f.close ()
						return data;
					

					return "".join (
						open (found_path ['find'], "r").readlines ()
					)
					
					
					
		except Exception as E:
			print (E)
			return 'exception occurred'
	
		return 'not found'

	
	def run (limit, loop):
		if (loop >= limit):
			print ("An available port could not be found; The process is exiting.");
			exit ()
	
		try:		
			port = start_at_port - 1 + loop
			print (f"run attempt { loop } of { limit }:", port)
			
			unavailable = is_port_in_use (port)
			#print ("unavailable:", unavailable)
			
			if (unavailable):
				raise Exception ("unavailable")
		
			server = Process (
				target = app.run,
				args = (),
				kwargs = {
					"port": port
				}
			)
		
			print ('carbonado app started')
			return {
				"server": server,
				"port": port
			}
			
		except Exception as E:
			pass;
			
		loop += 1;	
		
		return run (
			limit,
			loop = loop
		)
	
	if (static_port == True):
		limit = 1;
	else:
		limit = 100
		
	return run (
		limit = limit,
		loop = 1
	)
