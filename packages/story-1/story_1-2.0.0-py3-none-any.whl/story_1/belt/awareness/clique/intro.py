






import story_1.belt.awareness.sockets.clique_group as clique_group
import story_1.belt.awareness.thermos._clique as _clique





def start ():
	import click
	@click.group ()
	def group ():
		pass
	
	
	'''
		belt sockets --port 65000
	'''
	import click
	@group.command ("make")
	#@click.option ('--port', '-np', default = '65000')
	def search ():	
		import os
		CWD = os.getcwd ();
		
		import story_1.belt.climate as belt_climate
		belt_climate.build (CWD)

		import story_1.belt.mongo as mongo_node
		mongo_node.start (
			param = {
				"directory": "",
				"port": "27107"
			}
		)

		return;
		
		
	
	group.add_command (clique_group.add ())
	group.add_command (_clique.add ())
	
	
	
	#group.add_command (belt_clique_tracks ())
	#group.add_command (belt_clique_socket ())
	#group.add_command (stage_clique ())
	
	#group ()
	
	return group




#
