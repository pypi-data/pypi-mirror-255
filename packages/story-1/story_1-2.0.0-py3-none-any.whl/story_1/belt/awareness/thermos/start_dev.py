
'''
	import story_1.belt.awareness.thermos.start_dev as flask_dev
'''

import story_1.belt.awareness.thermos as belt_flask

def start (port):
	print ('starting')
	
	app = belt_flask.build ()
	app.run (port = port)

	return;