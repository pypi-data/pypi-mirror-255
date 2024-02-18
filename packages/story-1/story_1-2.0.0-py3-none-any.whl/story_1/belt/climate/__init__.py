
'''
	import story_1.belt.climate as belt_climate
	offline_climate = belt_climate.retrieve ()
'''

import os
from os.path import dirname, join, normpath
import pathlib
import sys

climate = {
	"elected belt": {},
	"paths": {}
}

def build (
	CWD = None
):
	belt_path = str (normpath (join (CWD, "belt")))
	#belt = str (normpath (join (CWD, "belt")))

	

	#if (os.path.isdir (offline_goods) != True):
	#	os.mkdir (offline_goods)
		
	if (os.path.isdir (belt_path) != True):
		os.mkdir (belt_path)
		print ("The belt was made.")
	else:
		print ()
		print ("There's already something at the path of the belt.")
		print (belt_path)
		print ()

	#climate ["paths"] ["offline_good"] = offline_goods
	climate ["paths"] ["belt"] = belt_path
	

	return;


def retrieve ():
	return climate