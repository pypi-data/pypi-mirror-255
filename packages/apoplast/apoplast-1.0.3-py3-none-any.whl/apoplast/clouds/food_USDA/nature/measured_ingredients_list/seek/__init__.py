
'''
import apoplast.clouds.food_USDA.nature.measured_ingredients_list.seek as mil_seek
mil_seek.eloquently ("Potassium, K", measured_ingredients_list)
'''

import apoplast.clouds.food_USDA.nature.measured_ingredients_list.for_each as mil_for_each

def eloquently (name, measured_ingredients_list):
	name = name.lower ()

	def action (ingredient):
		nonlocal name;
	
		if (ingredient ["name"].lower () == name):
			return False
			
		return True

	return mil_for_each.start (
		measured_ingredients_list = measured_ingredients_list,
		action = action
	)
	
start = eloquently
