


'''
	from story_1.modules.EEC_448_1.public_key.scan import scan_public_key
	[ public_key_instance, public_key_bytes, public_key_string ] = scan_public_key (public_key_path)
'''


#
#	https://pycryptodome.readthedocs.io/en/latest/src/public_key/ecc.html#Crypto.PublicKey.ECC.import_key
#

from Crypto.PublicKey import ECC


def scan_public_key (path):
	with open (path, mode = 'rb') as file:
		public_key_bytes = file.read ()
		
		public_key = ECC.import_key (
			public_key_bytes,
			curve_name = "Ed448"
		)
		
		public_key_string = public_key_bytes.hex ()

		return [ 
			public_key, 
			public_key_bytes, 
			public_key_string 
		];
		
	raise Exception ("")

