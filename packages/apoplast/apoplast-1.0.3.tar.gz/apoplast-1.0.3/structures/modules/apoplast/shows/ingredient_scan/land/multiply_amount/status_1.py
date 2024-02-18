


'''
	python3 insurance.py shows/ingredient_scan/land/multiply_amount/status_1.py
'''

import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import apoplast.clouds.food_USDA.examples as USDA_examples	
import apoplast.clouds.food_USDA.nature as food_USDA_nature
import apoplast.insure.equality as equality

import apoplast.shows.ingredient_scan.land.multiply_amount as multiply_land_amount
import apoplast.shows.ingredient_scan.grove.seek_name_or_accepts as grove_seek_name_or_accepts
	

import json	

def check_1 ():
	nature = food_USDA_nature.create (
		USDA_examples.retrieve ("branded/vegan_pizza_2672996.JSON")
	)

	ingredient_scan = nature ["essential nutrients"];
	grove = ingredient_scan ["grove"]
	essential_nutrient_measures = ingredient_scan ["measures"]

	'''
		60.018288 = 1351491697361075527451/22517998136852480000
		131.35 = 2627/20
	'''
	assert (
		ingredient_scan ["measures"] ==
		{
			'mass + mass equivalents': {
				'per recipe': {
					'grams': {
						'fraction string': '1484714659522158138277/45035996273704960000'
					}
				}
			}, 
			'energy': {
				'per recipe': {
					'food calories': {
						'fraction string': '2627/20'
					}
				}
			}
		}
	), ingredient_scan ["measures"]

	#print (json.dumps (essential_nutrient_measures, indent = 4))
	#return;

	
	iron = grove_seek_name_or_accepts.politely (
		grove = grove,
		name_or_accepts = "iron"
	)
	assert (
		iron ["measures"] ["mass + mass equivalents"] ["per recipe"] ["grams"] ["fraction string"] ==
		"89531560592125469/45035996273704960000"
	)


	multiply_land_amount.smoothly (
		land = ingredient_scan,
		amount = 2
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
						'fraction string': '1484714659522158138277/22517998136852480000'
					}
				}
			}, 
			'energy': {
				'per recipe': {
					'food calories': {
						'fraction string': '2627/10'
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
		"89531560592125469/22517998136852480000"
	)
	
	print (json.dumps (iron, indent = 4))
	
	return;
	
checks = {
	'check 1': check_1
}