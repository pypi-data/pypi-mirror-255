
'''
	python3 insurance.py clouds/food_USDA/nature/measured_ingredients_list/_status/status_volume_1.py
'''


import apoplast.clouds.food_USDA.examples as USDA_examples	
import apoplast.clouds.food_USDA.nature as food_USDA_nature
import apoplast.clouds.food_USDA.nature.measured_ingredients_list.seek as mil_seek

import apoplast.insure.equalities as equalities

import json	


def check_1 ():
	USDA_food_data = USDA_examples.retrieve ("branded/beet_juice_2412474.JSON")
	measured_ingredients_list = food_USDA_nature.create (
		USDA_food_data,
		return_measured_ingredients_list = True
	)

	print (json.dumps (measured_ingredients_list, indent = 4))
	
checks = {
	'check 1': check_1
}


