
'''
	python3 insurance.py shows/ingredient_scan_recipe/formulate/_status/status_food/status_0.py
'''



import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import apoplast.clouds.food_USDA.examples as USDA_examples	
import apoplast.clouds.food_USDA.nature as food_USDA_nature
import apoplast.insure.equality as equality
import apoplast.shows.ingredient_scan.grove.seek_name_or_accepts as grove_seek_name_or_accepts
import apoplast.shows.ingredient_scan_recipe.formulate as formulate_recipe

from copy import deepcopy
from fractions import Fraction
import json

def check_1 ():
	walnuts_1882785 = food_USDA_nature.create (
		USDA_examples.retrieve ("branded/walnuts_1882785.JSON")
	)
	
	'''
		recipe_1: {
			"mass + mass equivalents": {
				"per recipe": {
					"grams": {
						#
						#	424.0762244 grams
						#						
						"fraction string": "47746738154613173415299/112589990684262400000"
					}
				}
			},
			"energy": {
				"per recipe": {
					"food calories": {
						#
						#	3082.66 food calories
						#
						"fraction string": "154133/50"
					}
				}
			}
		}
	'''
	recipe_1 = formulate_recipe.adroitly ([
		[ walnuts_1882785, 1 ]
	])	
	assert ("cautionary ingredients" in recipe_1)
	assert ("natures" in recipe_1 ["cautionary ingredients"])
	
	assert (
		recipe_1 ["essential nutrients"] ["measures"] ==
		walnuts_1882785 ["essential nutrients"] [ "measures" ]
	), recipe_1
	
	
	recipe_2 = formulate_recipe.adroitly ([
		[ walnuts_1882785, 2 ]
	])
	assert (
		recipe_2 ["essential nutrients"] ["measures"] ==
		{
			"mass + mass equivalents": {
				"per recipe": {
					"grams": {
						#
						#	424.0762244 grams	
						#		-> 848.1524488 = 47746738154613173415299/56294995342131200000
						#						
						"fraction string": "47746738154613173415299/56294995342131200000"
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
						"fraction string": "154133/25"
					}
				}
			}
		}
	)
	
	
	
checks = {
	"check 1": check_1
}