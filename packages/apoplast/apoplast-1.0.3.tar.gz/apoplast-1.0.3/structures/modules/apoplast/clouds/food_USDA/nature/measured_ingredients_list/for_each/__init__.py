


'''
	import apoplast.clouds.food_USDA.nature.measured_ingredients_list.for_each as mil_for_each

	def action (ingredient):
		print (ingredient ["name"]
		return True;

	mil_for_each.start (
		measured_ingredients_list = measured_ingredients_list,
		action = action
	)
'''

'''
	#
	#	seek
	#

	import apoplast.clouds.food_USDA.nature.measured_ingredients_list.for_each as mil_for_each

	def action (ingredient):
		if (ingredient ["name"] == "Potassium, K"):
			return False
			
		return True

	mil_for_each.start (
		measured_ingredients_list = measured_ingredients_list,
		action = action
	)
'''

def action (ingredient):
	return True;

def eloquently (
	measured_ingredients_list = [],
	action = action
):
	for ingredient in measured_ingredients_list:
		advance = action (ingredient)
		if (not advance):
			return ingredient

	return None
	
start = eloquently