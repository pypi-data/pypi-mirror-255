
'''
	import story_1.modules.EEC_448_1.public_key.form as form_EEC_448_1_public_key
	public_key = form_EEC_448_1_public_key.smoothly (
		private_key_instance = None
	)
	public_key_instance = public_key ["instance"]
	public_key_DER_string = public_key ["DER"]
	public_key_hexadecimal_string = public_key ["hexadecimal"]
		
'''

import os

from Crypto.PublicKey.ECC import EccKey
from Crypto.PublicKey import ECC

import story_1.modules.EEC_448_1.private_key.scan as private_scan

def smoothly (
	private_key_instance = None
):	
	#private_key = private_scan.start (private_key_path)

	public_key_instance = private_key_instance.public_key ()
	public_key_DER_string = public_key_instance.export_key (format = "DER")
	
	public_key_hexadecimal_string = public_key_DER_string.hex ().upper ()
	assert (len (public_key_hexadecimal_string) == 138)
	assert (public_key_DER_string == bytes.fromhex (public_key_hexadecimal_string))
				
	return {
		"instance": public_key_instance,
		
		"DER": public_key_DER_string,
		"hexadecimal": public_key_hexadecimal_string
	}
