
'''
	python3 insurance.py clouds/food_USDA/nature/measured_ingredients_list/seek/status_1.py
'''

import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import apoplast.clouds.food_USDA.examples as USDA_examples
import json	
	
import apoplast.clouds.food_USDA.nature as food_USDA_nature
import apoplast.clouds.food_USDA.nature.measured_ingredients_list.seek as mil_seek

import apoplast.insure.equalities as equalities

def check_1 ():
	walnuts_1882785 = USDA_examples.retrieve ("branded/walnuts_1882785.JSON")
	assertions_foundational.run (walnuts_1882785)
	
	measured_ingredients_list = food_USDA_nature.create (
		walnuts_1882785,
		return_measured_ingredients_list = True
	)
	
	energy = mil_seek.eloquently ("energy", measured_ingredients_list)
	assert (type (energy) == dict)
	
	not_found = mil_seek.eloquently ("an ingredient not in the list", measured_ingredients_list)
	assert (not_found == None)

	
	print ("not_found", not_found)
	
checks = {
	'check 1': check_1
}