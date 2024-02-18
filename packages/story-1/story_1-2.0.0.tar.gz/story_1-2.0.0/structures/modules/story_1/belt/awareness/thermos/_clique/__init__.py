



import story_1.belt.awareness.thermos.start_dev as flask_start_dev

import os
from os.path import dirname, join, normpath
import pathlib
import sys
		
def add ():
	import click
	@click.group ("thermos")
	def group ():
		pass

	'''
		belt thermos start --label belt_1 --service-port 50000 --mongo-port 50001
	'''
	import os
	import click
	@group.command ("start")
	@click.option ('--label', default = 'belt')
	@click.option ('--service-port', '-sp', default = '50000')
	@click.option ('--mongo-port', '-mp', default = '50001')
	def search (label, service_port, mongo_port):	
	
		import sys
		from os.path import dirname, join, normpath
		import pathlib
		CWD = os.getcwd ();
		mongo_DB_directory = str (normpath (join (CWD, label, "mongo_DB_directory")))
		belt_path = str (normpath (join (CWD, label)))
		
		import story_1.belt.climate as belt_climate
		belt_climate.build (
			belt_path = belt_path
		)
		
		if (not os.path.exists (mongo_DB_directory)):			
			os.mkdir (mongo_DB_directory) 
			
		if (not os.path.isdir (mongo_DB_directory)):
			print ("There is already something at:", mongo_DB_directory)
			return;
		
		from multiprocessing import Process
		
		import story_1.belt.mongo as belt_mongo
		mongo = Process (
			target = belt_mongo.start,
			args = (),
			kwargs = {
				"params": {
					"DB_directory": mongo_DB_directory,
					"port": str (mongo_port)
				}
			}
		)
		mongo.start ()
	

		flask_server = Process (
			target = flask_start_dev.start,
			args = (),
			kwargs = {
				"port": service_port
			}
		)
		flask_server.start ()
		
	
		import time
		while True:
			time.sleep (1000)
	
		return;


	'''
		belt thermos create_safe --label belt-1
	'''
	import click
	@group.command ("create_safe")
	@click.option ('--label', required = True)
	@click.option ('--port', '-np', default = '50000')
	def search (label, port):	
		address = f"http://127.0.0.1:{ port }"
	
		import json
		from os.path import dirname, join, normpath
		import os
		import requests
		r = requests.patch (
			address, 
			data = json.dumps ({
				"label": "create safe",
				"fields": {
					"label": label
				}
			})
		)
		print (r.text)
		
		return;
		
	return group




#



