

'''
	python3 insurance.py shows/ingredient_scan/land/build/status_cautionary_1.py
'''

import json

def check_1 ():
	import apoplast.shows.ingredient_scan.DB.path as DB_paths
	import apoplast.shows.ingredient_scan.DB.access as access
	cautions_DB = access.DB (
		path = DB_paths.find (DB = "cautions")
	)
	
	import apoplast.shows.ingredient_scan.land.build as build_ingredient_scan_land
	land = build_ingredient_scan_land.eloquently (
		ingredients_DB = cautions_DB
	)
	
	#import rich
	#rich.print_json (data = land)

	import apoplast.shows.ingredient_scan.grove.seek_name_or_accepts as grove_seek_name_or_accepts
	trans_fat = grove_seek_name_or_accepts.politely (
		grove = land ["grove"],
		name_or_accepts = "trans fat"
	)
	assert (type (trans_fat) == dict)


	return;
	
	
	
checks = {
	"check 1": check_1
}