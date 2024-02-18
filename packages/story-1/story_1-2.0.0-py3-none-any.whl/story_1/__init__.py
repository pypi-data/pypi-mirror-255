


import pathlib
print ("story 1 @:", pathlib.Path (__file__).parent.resolve ())

import story_1._clique as clique

def start_clique ():
	group = clique.intro ()
	group ()