


'''
	caution, not checked.

		import apoplast.shows.ingredient_scan.DB.access as access
		import apoplast.shows.ingredient_scan.DB.sculpt.add as add_essential_nutrient
		add_essential_nutrient.eloquently (
			essentials_DB = access.DB (),
			essential = {
				"names": [],
				"accepts": [],
				"includes": []			
			}
		)
'''

import apoplast.shows.ingredient_scan.DB.access as access
import apoplast.shows.ingredient_scan.DB.scan.seek_next_region as seek_next_region

def eloquently (
	essentials_DB = access.DB (),
	essential = {}
):
	next_region = seek_next_region.politely (
		essentials_DB = essentials_DB
	)
	
	essential ["region"] = next_region
	id = essentials_DB.insert (essential)
	assert (type (id) == int)
	
	return id;