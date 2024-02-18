
'''
	#
	#	essentials
	#
	import apoplast.shows.ingredient_scan.land.build as build_ingredient_scan_land
	land = build_ingredient_scan_land.eloquently ()
'''

'''
	#
	#	cautionary
	#
	import apoplast.shows.ingredient_scan.DB.path as DB_paths
	import apoplast.shows.ingredient_scan.DB.access as access
	cautions_DB = access.DB (
		path = DB_paths.find (DB = "cautions")
	)
	
	import apoplast.shows.ingredient_scan.land.build as build_ingredient_scan_land
	land = build_ingredient_scan_land.eloquently (
		ingredients_DB = cautions_DB
	)
'''

'''
	plan:
		1. 	build the grove of essential nutrients 
			from the essential nutrients DB
		
		2. 
'''

import apoplast.shows.ingredient_scan.grove.nurture as grove_nurture
import apoplast.shows.ingredient_scan.land.build.measures as build_land_measures
	
import apoplast.shows.ingredient_scan.DB.access as access	
	
def eloquently (
	ingredients_DB = access.DB ()
):

	'''
	"joules": {
		"fraction string": "0"
	}
	'''
	return {
		"natures": [],
		"measures": build_land_measures.quickly (),
		"grove": grove_nurture.beautifully (
			ingredients_DB = ingredients_DB
		),
		"exclusions": []
	}