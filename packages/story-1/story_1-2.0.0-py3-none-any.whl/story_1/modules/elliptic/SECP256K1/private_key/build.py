



'''
	#
	#	write private key to path
	#
	
	
	#
	#	ABCDEFGHIJKLM
	#	NOPQRSTUVWXYZ
	#
	#	ABCDEFGHIJKLM NOP -> using these 16 letters as a seed? 
	#
	#	seed length = 114 nibbles
	#				=  57 bytes
	#
	seed = "4986888b11358bf3d541b41eea5daece1c6eff64130a45fc8b9ca48f3e0e02463c99c5aedc8a847686d669b7d547c18fe448fc5111ca88f4e8"
	format = "PEM"
	path = ""
	
	import story_1.modules.EEC_448_1.private_key.creator as EEC_448_1_private_key_creator
	private_key = EEC_448_1_private_key_creator.create (seed, format, path)
	private_key_instance = private_key ["instance"]
	private_key_string = private_key ["string"]
		
'''

'''
	seed:
		4986888b11358bf3d541b41eea5daece1c6eff64130a45fc8b9ca48f3e0e02463c99c5aedc8a847686d669b7d547c18fe448fc5111ca88f4e8
		5986888b11358bf3d541b41eea5daece1c6eff64130a45fc8b9ca48f3e0e02463c99c5aedc8a847686d669b7d547c18fe448fc5111ca88f4e8
		4986888B11358BF3D541B41EEA5DAECE1C6EFF64130A45FC8B9CA48F3E0E02463C99C5AEDC8A847686D669B7D547C18FE448FC5111CA88F4E8
		
	format:
		DER
		PEM
'''

'''
	https://pycryptodome.readthedocs.io/en/latest/src/public_key/ecc.html
'''
from Crypto.PublicKey.ECC import EccKey
import os.path


import ecdsa
import os

def create (
	seed, 
	format, 
	
	path = "",
	curve = "Ed448"
):	
    curve = ecdsa.SECP256k1
