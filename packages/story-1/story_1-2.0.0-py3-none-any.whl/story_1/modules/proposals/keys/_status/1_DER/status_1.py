
'''
	python3 insurance.proc.py "modules/proposals/keys/_status/1_DER/status_1.py"
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
	seed = "4986888b11358bf3d541b41eea5daece1c6eff64130a45fc8b9ca48f3e0e02463c99c5aedc8a847686d669b7d547c18fe448fc5111ca88f4e8"

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
				"format": "DER",
				"path": normpath (join (temporary_directory, "proposal.private_key.DER"))
			},
			"public key": {
				"format": "DER",
				"path": normpath (join (temporary_directory, "proposal.public_key.DER"))
			}
		}
	)
	
	
	

	return;
	
checks = {
	'check 1': check_1
}