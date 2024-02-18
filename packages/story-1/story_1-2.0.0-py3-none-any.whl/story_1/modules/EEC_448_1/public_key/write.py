



'''
	import story_1.modules.EEC_448_1.public_key.write as write_EEC_448_1_public_key
	write_EEC_448_1_public_key.smoothly (
		path = "",
		key_string = "",
		format = ""
	)
'''

import os

def smoothly (path, key_string, format):
	if (os.path.exists (path)):
		raise Exception (
			f"The path for the public key '{ path }' is not available."
		)
	
	if (format == "DER"):
		f = open (path, 'wb')
	elif (format in [ "PEM", "hexadecimal" ]):
		f = open (path, 'w')
	else:
		raise Exception (f"format '{ format }' was not accounted for.")
	
	f.write (key_string)
	f.close ()
	
