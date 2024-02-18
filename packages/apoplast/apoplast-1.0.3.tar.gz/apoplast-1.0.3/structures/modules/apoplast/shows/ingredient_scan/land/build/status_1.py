

'''
	python3 insurance.py shows/ingredient_scan/land/build/status_1.py
'''

import apoplast.shows.ingredient_scan.land.build as build_ingredient_scan_land
import json

def check_1 ():
	land = build_ingredient_scan_land.eloquently ()

	#print (json.dumps (land, indent = 4))

	return;
	
	
	
checks = {
	"check 1": check_1
}