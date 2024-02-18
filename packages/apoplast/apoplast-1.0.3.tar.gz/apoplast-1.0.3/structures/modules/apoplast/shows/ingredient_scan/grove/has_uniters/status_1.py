


'''
	python3 insurance.py shows/ingredient_scan/grove/has_uniters/status_1.py
'''

import json
import apoplast.shows.ingredient_scan.grove.has_uniters as has_uniters
import apoplast.shows.ingredient_scan.land.add_measured_ingredient as add_measured_ingredient
import apoplast.shows.ingredient_scan.land.build as build_ingredient_scan_land

def check_1 ():	
	land = build_ingredient_scan_land.eloquently ()	
	grove = land ["grove"]

	add_measured_ingredient.beautifully (
		land = land,
		
		amount = "1",
		source = {
			"name":	"",
			"FDC ID": "",
			"UPC": "",
			"DSLD ID": ""
		},
		measured_ingredient = {
			"name": "dietary fiber",
			"measures": {
				"mass + mass equivalents": {
					"per package": {
						"listed": [
							"1947.660",
							"mg"
						],
						"grams": {
							"decimal string": "1.948",
							"fraction string": "97383/50000"
						}
					}
				}
			}
		}
	)

	unity = has_uniters.check (grove, return_problem = True)
	assert ("dietary fiber" in unity ["problem"]["info"]["names"]) 
	
checks = {
	'check 1': check_1
}