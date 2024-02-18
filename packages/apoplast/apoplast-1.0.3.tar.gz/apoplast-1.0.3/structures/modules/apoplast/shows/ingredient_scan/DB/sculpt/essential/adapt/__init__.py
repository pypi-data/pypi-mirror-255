

'''
	caution, not checked.

		import apoplast.shows.ingredient_scan.DB.access as access
		import apoplast.shows.ingredient_scan.DB.sculpt.adapt as adapt_essential_nutrient
		adapt_essential_nutrient.eloquently (
			essentials_DB = access.DB (),
			essential = {
				"region": 1,
				"names": [ "protein" ],
				"accepts": [],
				"includes": []			
			}
		)
'''

import apoplast.shows.ingredient_scan.DB.access as access
import apoplast.shows.ingredient_scan.DB.scan.seek_next_region as seek_next_region
import apoplast.shows.ingredient_scan.DB.scan.seek as seek_nutrient

from tinydb import TinyDB, Query

import json

def eloquently (
	essentials_DB = access.DB (),
	essential = {}
):
	region = essential ["region"]
	
	revenue = essentials_DB.update (
		essential, 
		Query ().region == region
	)
		
	nutrient = seek_nutrient.presently (
		for_each = lambda essential : True if essential ["region"] == region else False
	)
	
	print ("adapted version =", json.dumps (nutrient, indent = 4))
		