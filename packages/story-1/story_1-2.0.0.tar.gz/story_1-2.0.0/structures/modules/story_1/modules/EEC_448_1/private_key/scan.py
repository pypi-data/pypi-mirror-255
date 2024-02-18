


'''
	import story_1.modules.EEC_448_1.private_key.scan as private_scan
	private_key = private_scan.start (path)
'''

from Crypto.PublicKey import ECC
from fractions import Fraction

def start (path):
	with open (path, mode = 'rb') as file:
		private_key_bytes = file.read ()
		private_key_instance = ECC.import_key (
			private_key_bytes,
			curve_name = "Ed448"
		)
		private_key_string = private_key_bytes.hex ()

		class private_key:
			def __init__ (this, instance):
				this.instance = instance
			
		return private_key (
			private_key_instance
		)

		return {
			"bytes": private_key_bytes,
			"instance": private_key_instance,
			"string": private_key_string
		}

