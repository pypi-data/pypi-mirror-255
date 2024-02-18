
'''
	
'''

'''
	create_belt
	
	fields {
		"label": ""
	}
'''

'''
	(mo)net
	monay
	monayuh
	monaym
'''

import story_1.belt.climate as belt_climate

import os
from os.path import dirname, join, normpath
import pathlib
import sys

def play (JSON):
	print ('create belt', JSON)
	offline_climate = belt_climate.retrieve ()

	belts_paths = offline_climate ["paths"] ["belt"]
	fields = JSON ["fields"]
	
	if ("label" not in fields):
		return {
			"obstacle": f'Please choose a "label" for the belt.'
		}
	
	belt_label = fields ["label"]
	belt_path = str (normpath (join (belts_paths, belt_label)))

	if (os.path.isdir (belt_path) != True):
		os.mkdir (belt_path)
		belt_climate.climate ["elected belt"] ["path"] = belt_path
		return {
			"victory": "belt created"
		}
		
	else:
		belt_climate.climate ["elected belt"] ["path"] = belt_path
		return {
			"obstacle": "There is already a directory at that path"
		}
