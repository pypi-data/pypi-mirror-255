







'''
	python3 insurance.py shows/ingredient_scan_recipe/formulate/_status/status_food/status_3.py
'''

import ships

import apoplast.insure.equality as equality

import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import apoplast.clouds.food_USDA.examples as USDA_examples	
import apoplast.clouds.food_USDA.nature as food_USDA_nature

import apoplast.shows.ingredient_scan.grove.seek_name_or_accepts as grove_seek_name_or_accepts
import apoplast.shows.ingredient_scan_recipe.formulate.assertions.ingredient as ingredient_assertion
import apoplast.shows.ingredient_scan_recipe.formulate as formulate_recipe

import json
from fractions import Fraction
from copy import deepcopy

def find_grams (measures):
	return Fraction (
		measures ["mass + mass equivalents"] ["per recipe"] ["grams"] ["fraction string"]
	)

def check_1 ():
	food_1 = food_USDA_nature.create (
		USDA_examples.retrieve ("branded/walnuts_1882785.JSON")
	)
	food_2 = food_USDA_nature.create (
		USDA_examples.retrieve ("branded/vegan_pizza_2672996.JSON")
	)

	recipe = formulate_recipe.adroitly ([
		[ food_1, 1 ],
		[ food_2, 1 ]
	])
	
	import apoplast.shows.ingredient_scan.grove.seek_measured_ingredient_name as grove_seek_measured_ingredient_name
	protein = grove_seek_measured_ingredient_name.politely (
		grove = recipe ["essential nutrients"] ["grove"],
		measured_ingredient_name = "protein"
	)
	
	'''
		grove measures: {
			"mass + mass equivalents": {
				"per recipe": {
					"grams": {
						"fraction string": "102917049606837137521983/225179981368524800000"
					}
				}
			}
		}

		protein: {
			"measures": {
				"mass + mass equivalents": {
					"per recipe": {
						"grams": {
							"fraction string": "15056569382213862513/225179981368524800"
						}
					},
					"portion of grove": {
						"fraction string": "161898595507675941000/1106634942009001478731"
					}
				}
			}
		}
	'''
	
	'''
		str ((Fraction ("456528486851663599/7036874417766400") + Fraction ("89531560592125469/45035996273704960")) / Fraction ("102917049606837137521983/225179981368524800000"))
			= '161898595507675941000/1106634942009001478731'
	'''
	assert (
		protein ["measures"]["mass + mass equivalents"]["portion of grove"]["fraction string"] ==
		"161898595507675941000/1106634942009001478731"
	), protein
	
	ships.show ("grove measures:", recipe ["essential nutrients"] ["measures"])
	ships.show ("protein:", protein)
	
checks = {
	"check 1": check_1
}