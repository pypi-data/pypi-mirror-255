
'''
	python3 insurance.proc.py "modules/proposals/keys/_status/3_hexadecimal_keys/status_1.py"
'''

from os.path import dirname, join, normpath
import pathlib
import sys
import os

import story_1.modules.proposals.keys.form as form_proposal_keys

import shutil

def erase_directory (directory_path):
	try:
		shutil.rmtree (directory_path)
	except Exception:
		pass;

def check_1 ():
	seed = "4986888B11358BF3D541B41EEA5DAECE1C6EFF64130A45FC8B9CA48F3E0E02463C99C5AEDC8A847686D669B7D547C18FE448FC5111CA88F4E8"

	this_directory = pathlib.Path (__file__).parent.resolve ()
	temporary_directory = normpath (join (this_directory, "temporary"))
	
	erase_directory (temporary_directory)
	os.mkdir (temporary_directory)
	
	form_proposal_keys.smoothly (
		utilizes = {
			"seed": seed
		},
		builds = {
			"seed": {
				"path": normpath (join (temporary_directory, "proposal.seed"))
			},
			"private key": {
				"format": "hexadecimal",
				"path": normpath (join (temporary_directory, "proposal.private_key.hexadecimal"))
			},
			"public key": {
				"format": "hexadecimal",
				"path": normpath (join (temporary_directory, "proposal.public_key.hexadecimal"))
			}
		}
	)
	
	
	

	return;
	
checks = {
	'check 1': check_1
}