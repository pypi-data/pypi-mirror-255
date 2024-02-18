

import os
import time
import json
# os.getcwd()

import carbonado
import carbonado.climate as climate
	


def clique ():

	print ('starting clique')

	import click
	@click.group (invoke_without_command = True)
	@click.pass_context
	def group (ctx):
		if ctx.invoked_subcommand is None:
			#click.echo ('Clique was invoked without a subcommand.')
			start ([], standalone_mode = False)
		else:
			#click.echo ('Clique was invoked with the subcommand: %s' % ctx.invoked_subcommand)
			pass;
	
		pass

	the_climate = climate.scan ();
	preconfigured_extensions = the_climate ["preconfigured extensions"]

	# https://stackoverflow.com/questions/47631914/how-to-pass-several-list-of-arguments-to-click-option
	def parse_extensions (option):	
		try:
			option = json.loads (option)
			# option = str(option)  # this also works
		except ValueError:
			print ("ValueError:", ValueError)
			pass

		option = option [1:-1]  # trim '[' and ']'
		options = option.split (',')

		print ("options:", options)

		for i, value in enumerate (options):
			try:
				int(value)
			except ValueError:
				options[i] = value
			else:
				options[i] = int(value)
			
		trimmed_options = [string.strip() for string in options]
			
		return trimmed_options;

	'''
		carbonado carbonado --extensions [.s.HTML,.jpg,.png]
		carbonado carbonado --extensions "[ .s.HTML, .jpg, .png ]"
	'''
	import click
	@click.command ("carbonado")
	@click.option ('--extensions', default = preconfigured_extensions)
	@click.option ('--port', default = 6789)
	@click.option ('--static-port', is_flag = True, default = False)
	@click.option ('--verbose', default = 1)
	def internal_start (extensions, port, static_port, verbose):
		print ("carbonado")
		print ("extensions:", type (extensions), extensions)
		
		parsed_extensions = parse_extensions (extensions);
		
		
	
		print ("parsed exetnsions:", parsed_extensions)
	
		import pathlib
		from os.path import dirname, join, normpath
		this_dir = str (pathlib.Path (__file__).parent.resolve ())
	
		carbonado.start ({
			"directory": this_dir,
			"relative path": this_dir,
			
			"port": port,
			"static port": static_port,
			"verbose": verbose,
			
			"extensions": parsed_extensions
		})
		
		# close = input ("press close to exit") 
		while True:                                  
			time.sleep (1)  

	'''
		carbonado start --port 2345 --static-port
	'''
	import click
	@click.command ("start")
	@click.option ('--extensions', default = preconfigured_extensions)
	@click.option ('--port', default = 2345)
	@click.option ('--static-port', is_flag = True, default = False)
	def start (extensions, port, static_port):	
		parsed_extensions = parse_extensions (extensions)
	
		carbonado.start ({
			"directory": os.getcwd (),
			"relative path": os.getcwd (),
			
			"port": port,
			"static port": static_port,
			"verbose": 1,
			
			"extensions": parsed_extensions
		})
		
		# close = input ("press close to exit") 
		while True:                                  
			time.sleep (1)  

	group.add_command (internal_start)
	group.add_command (start)

	#start ([], standalone_mode=False)

	#group.add_command (clique_group ())
	group ()


	#start ()
	                          
