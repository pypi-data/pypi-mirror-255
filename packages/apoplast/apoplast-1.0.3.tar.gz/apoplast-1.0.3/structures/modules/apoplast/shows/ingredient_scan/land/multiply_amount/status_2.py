


'''
	python3 insurance.py shows/ingredient_scan/land/multiply_amount/status_2.py
'''

import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import apoplast.clouds.food_USDA.examples as USDA_examples	
import apoplast.clouds.food_USDA.nature as food_USDA_nature
import apoplast.insure.equality as equality

import apoplast.shows.ingredient_scan.land.multiply_amount as multiply_land_amount
import apoplast.shows.ingredient_scan.grove.seek_name_or_accepts as grove_seek_name_or_accepts

from fractions import Fraction

import json	

def check_1 ():
	nature = food_USDA_nature.create (
		USDA_examples.retrieve ("branded/walnuts_1882785.JSON")
	)

	ingredient_scan = nature ["essential nutrients"];
	grove = ingredient_scan ["grove"]
	essential_nutrient_measures = ingredient_scan ["measures"]

	amount = 9;

	'''
		60.018288 = 1351491697361075527451/22517998136852480000
		131.35 = 2627/20
	'''
	mass_and_mass_eq_grams_per_package = Fraction ("47746738154613173415299/112589990684262400000")
	energy_food_calories_per_package = Fraction ("154133/50")
	
	assert (
		ingredient_scan ["measures"] ==
		{
			'mass + mass equivalents': {
				'per recipe': {
					'grams': {
						'fraction string': str (mass_and_mass_eq_grams_per_package)
					}
				}
			}, 
			'energy': {
				'per recipe': {
					'food calories': {
						'fraction string': str (energy_food_calories_per_package)
					}
				}
			}
		}
	), ingredient_scan ["measures"]

	#print (json.dumps (essential_nutrient_measures, indent = 4))
	#return;

	
	iron_amount_per_package = Fraction ("1461913475040736643/112589990684262400000")
	
	iron = grove_seek_name_or_accepts.politely (
		grove = grove,
		name_or_accepts = "iron"
	)
	assert (
		iron ["measures"] ["mass + mass equivalents"] ["per recipe"] ["grams"] ["fraction string"] ==
		str (iron_amount_per_package)
	), iron


	multiply_land_amount.smoothly (
		land = ingredient_scan,
		amount = amount
	)
	
	'''
		120.036576 = 1351491697361075527451/11258999068426240000
		262.7 = 2627/10
	'''
	assert (
		ingredient_scan ["measures"] ==
		{
			'mass + mass equivalents': {
				'per recipe': {
					'grams': {
						'fraction string': str (mass_and_mass_eq_grams_per_package * amount)
					}
				}
			}, 
			'energy': {
				'per recipe': {
					'food calories': {
						'fraction string': str (energy_food_calories_per_package * amount)
					}
				}
			}
		}
	), ingredient_scan ["measures"]

	
	iron = grove_seek_name_or_accepts.politely (
		grove = grove,
		name_or_accepts = "iron"
	)
	assert (
		iron ["measures"] ["mass + mass equivalents"] ["per recipe"] ["grams"] ["fraction string"] ==
		str (iron_amount_per_package * 9)
	)
	
	print (json.dumps (iron, indent = 4))
	
	return;
	
checks = {
	'check 1': check_1
}