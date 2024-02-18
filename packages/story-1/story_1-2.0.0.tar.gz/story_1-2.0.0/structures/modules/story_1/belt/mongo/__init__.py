

'''
	import story_1.belt.mongo as belt_mongo
	belt_mongo.start (
		param = {
			"directory": "",
			"port": "27107"
		}
	)
'''


'''
	mongod --dbpath ./mongo_DB --port 27018
'''
import law_dictionary

import subprocess
def start (
	params = {}
):
	law_dictionary.check (	
		allow_extra_fields = True,
		laws = {
			"DB_directory": {
				"required": True,
				"type": str
			},
			"port": {
				"required": True,
				"type": str
			}
		},
		dictionary = params
	)

	port = params ["port"]
	DB_directory = params ["DB_directory"]

	subprocess.run (
		f"mongod --dbpath '{ DB_directory }' --port '{ port }'", 
		shell = True, 
		check = True
	)