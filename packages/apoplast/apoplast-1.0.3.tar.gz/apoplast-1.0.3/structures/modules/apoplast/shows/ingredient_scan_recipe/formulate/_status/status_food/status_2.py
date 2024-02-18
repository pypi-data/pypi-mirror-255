





'''
	python3 insurance.py shows/ingredient_scan_recipe/formulate/_status/status_food/status_2.py
'''



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

	food_1_1 = deepcopy (food_1)
	food_2_1 = deepcopy (food_2)

	food_1_mass_and_mass_eq_grams = Fraction ("47746738154613173415299/112589990684262400000")
	food_1_energy_food_calories = Fraction ("154133/50")
	food_1_multiplier = 10

	food_2_mass_and_mass_eq_grams = Fraction ("1484714659522158138277/45035996273704960000")
	food_2_energy_food_calories = Fraction ("2627/20")
	food_2_multiplier = 100
		
	assert (
		food_1 ["essential nutrients"] ["measures"] ==
		{
			"mass + mass equivalents": {
				"per recipe": {
					"grams": {
						"fraction string": str (food_1_mass_and_mass_eq_grams)
					}
				}
			},
			"energy": {
				"per recipe": {
					"food calories": {
						"fraction string": str (food_1_energy_food_calories)
					}
				}
			}
		}
	), food_1 ["essential nutrients"] ["measures"]
	assert (
		food_2 ["essential nutrients"] ["measures"] ==
		{
			"mass + mass equivalents": {
				"per recipe": {
					"grams": {
						"fraction string": str (food_2_mass_and_mass_eq_grams)
					}
				}
			},
			"energy": {
				"per recipe": {
					"food calories": {
						"fraction string": str (food_2_energy_food_calories)
					}
				}
			}
		}
	), food_2 ["essential nutrients"] ["measures"]

	recipe = formulate_recipe.adroitly ([
		[ food_1, food_1_multiplier ],
		[ food_2, food_2_multiplier ]
	])
	
	assert (
		recipe ["essential nutrients"] ["measures"] ==
		{
			"mass + mass equivalents": {
				"per recipe": {
					"grams": {
						"fraction string": str (
							(food_1_mass_and_mass_eq_grams * food_1_multiplier) +
							(food_2_mass_and_mass_eq_grams * food_2_multiplier)							
						)
					}
				}
			},
			"energy": {
				"per recipe": {
					"food calories": {
						"fraction string": str (
							(food_1_energy_food_calories * food_1_multiplier) +
							(food_2_energy_food_calories * food_2_multiplier)							
						)
					}
				}
			}
		}
	), food_1 ["essential nutrients"] ["measures"]
	
	
	'''
	assert_ingredient ("protein")
	assert_ingredient ("carbohydrates")
	assert_ingredient ("Cholesterol")
	assert_ingredient ("Sodium, Na")
	'''
	
	ingredient_assertion.check (
		"carbohydrates",
		
		recipe,
		
		food_1_1,
		food_2_1,
		
		food_1_multiplier,
		food_2_multiplier,
		
		food_1,
		food_2
	)
	ingredient_assertion.check (
		"Cholesterol",
		
		recipe,
		
		food_1_1,
		food_2_1,
		
		food_1_multiplier,
		food_2_multiplier,
		
		food_1,
		food_2
	)
	ingredient_assertion.check (
		"protein",
		
		recipe,
		
		food_1_1,
		food_2_1,
		
		food_1_multiplier,
		food_2_multiplier,
		
		food_1,
		food_2
	)
	
checks = {
	"check 1": check_1
}