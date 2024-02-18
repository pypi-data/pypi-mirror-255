

'''
	python3 insurance.py shows/ingredient_scan/land/multiply_amount/status_loop_1.py
'''

import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import apoplast.clouds.food_USDA.examples as USDA_examples
import json	
	
import apoplast.clouds.food_USDA.nature as food_USDA_nature

import apoplast.insure.equality as equality

import apoplast.shows.ingredient_scan.land.multiply_amount as multiply_land_amount
	
def check_1 ():
	foods = [
		"branded/beet_juice_2412474.JSON",
		"branded/beet_juice_2642759.JSON",
		"branded/Gardein_f'sh_2663758.JSON",
		"branded/impossible_beef_2664238.JSON",
		"branded/vegan_pizza_2672996.JSON",	
		"branded/walnuts_1882785.JSON"
	]
	
	for food in foods:
		food_data = USDA_examples.retrieve (food)
		nature = food_USDA_nature.create (food_data)
		
		multiply_land_amount.smoothly (
			land = nature ["essential nutrients"],
			amount = 124892389
		)
		
		#print (json.dumps (nature ["essential nutrients"], indent = 4))
		
	
checks = {
	'check 1': check_1
}