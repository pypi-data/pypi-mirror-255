

'''
import apoplast.clouds.supp_NIH.nature.measured_ingredients.seek_name as seek_name
seek_name.beautifully (
	measured_ingredients,
	name
)
'''

import apoplast.clouds.supp_NIH.nature.measured_ingredients.seek as seek

def beautifully (measured_ingredients, name):
	def for_each (
		measured_ingredient, 
		indent = 0, 
		parent_measured_ingredient = None
	):
		return measured_ingredient ["name"] == name

	return seek.beautifully (
		measured_ingredients = measured_ingredients,
		for_each = for_each
	)

