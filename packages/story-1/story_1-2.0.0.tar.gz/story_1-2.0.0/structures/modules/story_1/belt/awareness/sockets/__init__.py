

'''
	https://pypi.org/project/websockets/
'''
import asyncio
from websockets.server import serve

import story_1.belt.options as options

'''
	
'''
async def handler (websocket):
	async def records (record):
		await websocket.send (record)

	async def obstacle (message):
		await websocket.send (json.dumps (message))

	async def victory (message):
		await websocket.send (json.dumps (message))



	async for message in websocket:
		
	
		await websocket.send ("The message is being processed.")
		print ("After the processing?")
		
		await websocket.send (f'The option is processing.')
	
		await options.play (
			JSON = message,
			records = records,
			obstacle = obstacle,
			victory = victory
		)
		

async def handler_2 (websocket):

	#await websocket.send ("handler_2")
	
	#connected.add (websocket)

	async for message in websocket:
		print ("message:", message)
	
		#websocket.broadcast(connected, "Hello!")
	
		await websocket.send ("The message is being processed.")
		await websocket.send ("The message is being processed 2.")
		
		print ("here?")
		

async def main (port):
	async with serve (handler_2, "localhost", port):
		#print ("socket opened on port", port)
	
		await asyncio.Future ()

def open (
	port = None
):
	

	
			
		

	asyncio.run (main (port))