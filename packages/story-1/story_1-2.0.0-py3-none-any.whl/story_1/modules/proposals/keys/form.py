





'''
	seed = "4986888b11358bf3d541b41eea5daece1c6eff64130a45fc8b9ca48f3e0e02463c99c5aedc8a847686d669b7d547c18fe448fc5111ca88f4e8"

	import story_1.modules.proposals.keys.form as form_proposal_keys
	form_proposal_keys.smoothly (
		#
		#	inputs, consumes, utilizes
		#
		utilizes = {
			"seed": seed
		},
		
		#
		#	outputs, produces, builds
		#
		builds = {
			"seed": {
				"path": ""
			},
			"private key": {
				"format": "",
				"path": ""
			},
			"public key": {
				"format": "",
				"path": ""
			}
		}
	)
'''

import story_1.modules.EEC_448_1.private_key.creator as EEC_448_1_private_key_creator

import story_1.modules.EEC_448_1.public_key.form as form_EEC_448_1_public_key
import story_1.modules.EEC_448_1.public_key.write as write_EEC_448_1_public_key
	

import os
def write_seed (path, seed_string):
	if (os.path.exists (path)):
		raise Exception (f"The path for the seed_string is not available. '{ path }'");
	
	#f = open (path, 'wb')
	f = open (path, 'w')
	f.write (seed_string)
	f.close ()
	
	return True	
	
def write_public_key (path, public_key_hexadecimal):
	if (os.path.exists (path)):
		raise Exception (f"The path for the public_key hexadecimal is not available. '{ path }'");
	
	f = open (path, 'w')
	f.write (public_key_hexadecimal)
	f.close ()
	
	return True		
	
'''
	#format = "PEM",
	format = "DER",
	#format = "raw",
	#format = "bytes",
'''
def smoothly (
	utilizes = {},
	builds = {}
):	
	assert ("seed" in utilizes)
	
	assert ("seed" in builds)
	assert ("path" in builds ["seed"])
	
	assert ("private key" in builds)
	assert ("format" in builds ["private key"])
	assert ("path" in builds ["private key"])
	
	assert ("public key" in builds)
	assert ("format" in builds ["public key"])
	assert ("path" in builds ["public key"])

	'''
		private key
	'''
	private_key = EEC_448_1_private_key_creator.create (
		utilizes ["seed"], 
		builds ["private key"] ["format"], 
		
		path = builds ["private key"] ["path"]
	)
	private_key_instance = private_key ["instance"]
	#private_key_string = private_key ["string"]
	
			
	
	'''
		public key
	'''
	public_key = form_EEC_448_1_public_key.smoothly (
		private_key_instance = private_key_instance
	)
	write_EEC_448_1_public_key.smoothly (
		path = builds ["public key"] ["path"],
		key_string = public_key ["hexadecimal"],
		format = "hexadecimal"
	)	

	
	write_seed (
		builds ["seed"] ["path"], 
		utilizes ["seed"]
	)