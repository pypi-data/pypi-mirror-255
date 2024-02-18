

'''
	caution, not checked.

		import apoplast.shows.ingredient_scan.DB.access as access
		import apoplast.shows.ingredient_scan.DB.sculpt.erase as erase_essential_nutrient
		erase_essential_nutrient.eloquently (
			essentials_DB = access.DB (),
			region = 1
		)
'''

import apoplast.shows.ingredient_scan.DB.access as access
import apoplast.shows.ingredient_scan.DB.scan.seek_next_region as seek_next_region
import apoplast.shows.ingredient_scan.DB.scan.seek as seek_nutrient

from tinydb import TinyDB, Query

import json

def eloquently (
	essentials_DB = access.DB (),
	region = 1
):	
	removal = essentials_DB.remove (Query ().region == region)
	print ("removal:", removal)
	
	#print ("adapted version =", json.dumps (nutrient, indent = 4))
		