
'''
	python3 insurance.py shows/ingredient_scan/land/add_measured_ingredient/status_m_eq_and_ba/status_1.py
'''

import apoplast.shows.ingredient_scan.land.add_measured_ingredient as add_measured_ingredient
import apoplast.shows.ingredient_scan.land.build as build_ingredient_scan_land
import apoplast.shows.ingredient_scan.grove.seek as grove_seek	

import json	
	
def check_1 ():
	land = build_ingredient_scan_land.eloquently ()	

	add_measured_ingredient.beautifully (
		land = land,
		
		amount = 10,
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
	
	add_measured_ingredient.beautifully (
		land = land,
		
		amount = 10,
		source = {
			"name":	"WALNUTS HALVES & PIECES, WALNUTS",
			"FDC ID": "1882785",
			"UPC": "099482434618",
			"DSLD ID": ""
		},
		measured_ingredient = {
			"name": "Vitamin D (D2 + D3), International Units",
			"measures": {
				"biological activity": {
					"per package": {
						"listed": [
							"0.000",
							"IU"
						],
						"IU": {
							"decimal string": "0.000",
							"fraction string": "0"
						}
					}
				}
			}
		}
	)

	Potassium = grove_seek.beautifully (
		grove = land ["grove"],
		for_each = (
			lambda entry : True if (
				"potassium, k" in list (map (
					lambda name : name.lower (), 
					entry ["info"] ["names"]
				))
			) else False
		)
	)
	assert (len (Potassium ["natures"]) == 1)
	assert (
		Potassium ["natures"][0] ==
		{
			"amount": "10",
			"source": {
				"name": "WALNUTS HALVES & PIECES, WALNUTS",
				"FDC ID": "1882785",
				"UPC": "099482434618",
				"DSLD ID": ""
			},
			"ingredient": {
				"name": "Potassium, K"
			},
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
	assert (
		Potassium ["measures"]["mass + mass equivalents"] ==
		{
			"per recipe": {
				"grams": {
					"fraction string": "97383/5000"
				}
			}
		}
	)


	Vitamin_D = grove_seek.beautifully (
		grove = land ["grove"],
		for_each = (
			lambda entry : True if (
				"Vitamin D (D2 + D3), International Units".lower () in list (map (
					lambda name : name.lower (), 
					entry ["info"] ["names"]
				))
			) else False
		)
	)
	assert (len (Vitamin_D ["natures"]) == 1)
	assert (
		Vitamin_D ["natures"][0] ==
		{
			"amount": "10",
			"source": {
				"name": "WALNUTS HALVES & PIECES, WALNUTS",
				"FDC ID": "1882785",
				"UPC": "099482434618",
				"DSLD ID": ""
			},
			"ingredient": {
				"name": "Vitamin D (D2 + D3), International Units",
			},
			"measures": {
				"biological activity": {
					"per package": {
						"listed": [
							"0.000",
							"IU"
						],
						"IU": {
							"decimal string": "0.000",
							"fraction string": "0"
						}
					}
				}
			}
		}
	), Vitamin_D ["natures"]
	assert (
		Vitamin_D ["measures"]["biological activity"] ==
		{
			"per recipe": {
				"IU": {
					"fraction string": "0"
				}
			}
		}
	)
	
	assert (
		land ["measures"] ["mass + mass equivalents"] ==
		{
			"per recipe": {
				"grams": {
					"fraction string": "0"
				}
			}
		}
	)
	

	return;
	
	
checks = {
	'check 1': check_1
}