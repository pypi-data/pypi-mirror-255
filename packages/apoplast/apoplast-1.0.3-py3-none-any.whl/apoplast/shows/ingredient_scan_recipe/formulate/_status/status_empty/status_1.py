



'''
	python3 insurance.py shows/ingredient_scan_recipe/formulate/_status/status_empty/status_1.py
'''



import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import apoplast.clouds.food_USDA.examples as USDA_examples	
import apoplast.clouds.food_USDA.nature as food_USDA_nature
import apoplast.insure.equality as equality

import apoplast.shows.ingredient_scan_recipe.formulate as formulate_recipe
import apoplast.shows.ingredient_scan.grove.seek_name_or_accepts as grove_seek_name_or_accepts


from copy import deepcopy
from fractions import Fraction
import json


def check_1 ():
	recipe_1 = formulate_recipe.adroitly ([])
	
	assert (
		recipe_1 ["essential nutrients"] ["measures"] ==
		{
			"mass + mass equivalents": {
				"per recipe": {
					"grams": {
						#
						#	424.0762244 grams	
						#		-> 848.1524488 = 47746738154613173415299/56294995342131200000
						#						
						"fraction string": "0"
					}
				}
			},
			"energy": {
				"per recipe": {
					"food calories": {
						#
						#	3082.66 food calories
						#		-> 6165.32 = 154133/25
						#
						"fraction string": "0"
					}
				}
			}
		}
	)
	
	
	
checks = {
	"check 1": check_1
}