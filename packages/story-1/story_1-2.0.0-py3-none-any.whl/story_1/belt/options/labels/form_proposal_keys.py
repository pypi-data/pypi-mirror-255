
'''
	{
		"label": "form proposal keys",
		"fields": {
			"seed": ""
		}
	}
'''

import story_1.belt.climate as belt_climate

def play (
	JSON
):
	paths = belt_climate ["paths"]

	fields = JSON ["fields"]
	seed = fields ["seed"]
	directory_path = fields ["directory_path"]

	print (
	
	)

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
				"path": normpath (join (directory_path, "proposal.seed"))
			},
			"private key": {
				"format": "hexadecimal",
				"path": normpath (join (directory_path, "proposal.private_key.hexadecimal"))
			},
			"public key": {
				"format": "hexadecimal",
				"path": normpath (join (directory_path, "proposal.public_key.hexadecimal"))
			}
		}
	)