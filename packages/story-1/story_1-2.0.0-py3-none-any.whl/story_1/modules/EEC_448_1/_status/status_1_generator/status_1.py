
'''
	python3 insurance.proc.py "modules/EEC_448_1/_status/status_1_generator/status_1.py"
'''


import story_1.modules.EEC_448_1.private_key.creator as EEC_448_1_private_key_creator
		
import pathlib
from os.path import dirname, join, normpath
import os

		
def check_1 ():
	seeds = [ 
		"4986888b11358bf3d541b41eea5daece1c6eff64130a45fc8b9ca48f3e0e02463c99c5aedc8a847686d669b7d547c18fe448fc5111ca88f4e8",
		"5986888b11358bf3d541b41eea5daece1c6eff64130a45fc8b9ca48f3e0e02463c99c5aedc8a847686d669b7d547c18fe448fc5111ca88f4e8",
		"000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",		
		"ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
		"123412341234123412341234123412341234123412341234123412341234123412341234123412341234123412341234123412341234123412",
		"0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f1e0f",	
		"135791357913579135791357913579135791357913579135791357913579135791357913579135791357913579135791357913579135791357",	
		"2468ef2468ef2468ef2468ef2468ef2468ef2468ef2468ef2468ef2468ef2468ef2468ef2468ef2468ef2468ef2468ef2468ef2468ef2468ef"	
	]
	formats = [ "DER", "PEM" ]
	
	for seed in seeds:
		for format in formats:
			private_key_path = normpath (
				join (pathlib.Path (__file__).parent.resolve (), "EEC_448_1_private_key")
			) + "." + format
			
			private_key = EEC_448_1_private_key_creator.create (
				seed, 
				format, 
				private_key_path
			)
			
			private_key_instance = private_key ["instance"]
			private_key_string = private_key ["string"]
				
			os.remove (private_key_path)

		
checks = {
	"elliptic private key generation": check_1
}