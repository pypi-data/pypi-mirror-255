

import os
import time
import json
# os.getcwd()

import carbonado
import carbonado.climate as climate

the_climate = climate.scan ();

# https://stackoverflow.com/questions/47631914/how-to-pass-several-list-of-arguments-to-click-option
def start (option):	
	if (option == None):
		return the_climate ["preconfigured extensions"];

	try:
		option = json.loads (option)
		# option = str(option)  # this also works
	except ValueError:
		#print ("ValueError:", ValueError)
		pass

	option = option [1:-1]  # trim '[' and ']'
	options = option.split (',')

	#print ("options:", options)

	for i, value in enumerate (options):
		try:
			int(value)
		except ValueError:
			options[i] = value
		else:
			options[i] = int(value)
		
	trimmed_options = [string.strip() for string in options]
		
	return trimmed_options;