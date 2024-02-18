
'''
	#
	#	write public key to path
	#
	import story_1.modules.EEC_448_1.public_key.creator as EEC_448_1_public_key_creator
	public_key = EEC_448_1_public_key_creator.create (
		private_key_path = "",
		
		public_key_path = "",
		public_key_format = ""
	)
	public_key_instance = public_key ["instance"]
	public_key_string = public_key ["string"]
		
'''

'''
	format:
		DER
		PEM
'''
import os

from Crypto.PublicKey.ECC import EccKey
from Crypto.PublicKey import ECC

import story_1.modules.EEC_448_1.private_key.scan as private_scan

def write_public_key (path, key_string, format):
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
	
	return True;


def create (
	private_key_path = "",
	public_key_path = "",
	public_key_format = ""
):	
	private_key = private_scan.start (private_key_path)

	if (public_key_format == "hexadecimal"):
		public_key_export_format = "DER"
	else:
		public_key_export_format = public_key_format

	public_key_instance = private_key.instance.public_key ()
	public_key_string = public_key_instance.export_key (
		format = public_key_export_format
	)
	
	if (public_key_format == "hexadecimal"):
		#
		#	https://stackoverflow.com/questions/6624453/whats-the-correct-way-to-convert-bytes-to-a-hex-string-in-python-3
		#
		#
		#	138 characters
		#
		public_key_hexadecimal_string = public_key_string.hex ()
		assert (len (public_key_hexadecimal_string) == 138)
		#print ("public key hexadecimal string:", public_key_hexadecimal_string)

		assert (
			bytes.fromhex (public_key_hexadecimal_string) == 
			public_key_string
		)
		
		public_key_string = public_key_hexadecimal_string 
		
	write_public_key (
		public_key_path, 
		
		public_key_string, 
		public_key_format
	)
			
	return {
		"instance": public_key_instance,
		"string": public_key_string
	}
