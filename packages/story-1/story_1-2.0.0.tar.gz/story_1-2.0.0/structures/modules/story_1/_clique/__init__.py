




#from story_1._clique.group import clique as clique_group

#import story_1.belt.awareness_sockets.clique_group as clique_group
#from story_1.belt.clique_tracks import clique as belt_clique_tracks
#from story_1.belt.clique_socket import clique as belt_clique_socket


def intro ():

	import click
	@click.group ()
	def group ():
		pass

	import click
	@click.command ("tutorial")
	def sphene_command ():	
		import pathlib
		from os.path import dirname, join, normpath
		this_directory = str (pathlib.Path (__file__).parent.resolve ())
		module_directory = str (normpath (join (this_directory, "..")));

		import sphene
		sphene.start ({
			"extension": ".s.HTML",
			
			#
			#	This is the node from which the traversal occur.
			#
			"directory": module_directory,
			
			#
			#	This path is removed from the absolute path of share files found.
			#
			"relative path": module_directory
		})
		
		import time
		while True:
			time.sleep (1000)

	group.add_command (sphene_command)
	
	
	#group.add_command (clique_group.add ())
	
	
	#group.add_command (vibes_clique ())
	
	
	return group;




#
