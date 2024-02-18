

'''
	python3 insurance.py shows/ingredient_scan/land/add_measured_ingredient/status_empty_grove/status_1.py
'''

import apoplast.shows.ingredient_scan.land.add_measured_ingredient as add_measured_ingredient
import apoplast.shows.ingredient_scan.land.build as build_ingredient_scan_land
import apoplast.shows.ingredient_scan.grove.seek as grove_seek	
	
	
import json	
	
def check_1 ():
	land = build_ingredient_scan_land.eloquently ()	
	land ["grove"] = []

	added = add_measured_ingredient.beautifully (
		land = land,
		
		amount = "1",
		source = {
			"name":	"WALNUTS HALVES & PIECES, WALNUTS",
			"FDC ID": "1882785",
			"UPC": "099482434618",
			"DSLD ID": ""
		},
		measured_ingredient = {
			"name": "Potassium, K",
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
	
	assert (added == False)
		
	print (land ["grove"])
	


	return;
	
	
checks = {
	'check 1': check_1
}