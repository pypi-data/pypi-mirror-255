



import story_1.belt.awareness.thermos.start_dev as flask_start_dev

import os
from os.path import dirname, join, normpath
import pathlib
import sys
		
import asyncio
from websockets.sync.client import connect

async def async_search (port):
	address = f"ws://localhost:{ port }"
	
	with connect (address) as websocket:
		websocket.send ("Hello world!")
		message = websocket.recv ()
		
		print (f"Received: {message}")

	
		
def add ():
	import click
	@click.group ("sockets")
	def group ():
		pass


	'''
		./story_1 belt sockets --port 65000
	'''
	import click
	@group.command ("sockets")
	@click.option ('--port', '-np', default = '65000')
	def search (port):	
		CWD = os.getcwd ();
		
		import story_1.belt.climate as belt_climate
		belt_climate.build (
			CWD
		)
	
		belt_sockets.open (
			port = port
		)
	
		return;

	'''
		story_1_local sockets make_pouch --label belt-1
	'''
	import click
	@group.command ("make_belt")
	@click.option ('--label', required = True)
	@click.option ('--port', '-np', default = '65000')
	def search (label, port):	
		
		asyncio.run (async_search (port))	
		
	return group




#



