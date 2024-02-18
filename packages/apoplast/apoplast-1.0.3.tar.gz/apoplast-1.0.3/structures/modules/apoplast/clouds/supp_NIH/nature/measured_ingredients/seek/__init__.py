



'''
	import apoplast.clouds.supp_NIH.nature.measured_ingredients.seek as seek

	def for_each (
		measured_ingredient, 
		indent = 0, 
		parent_measured_ingredient = None
	):
		print (measured_ingredient ["name"]
		return False;

	seek.beautifully (
		measured_ingredients = measured_ingredients,
		for_each = for_each
	)
'''


def for_each (
	measured_ingredient, 
	indent = 0, 
	parent_measured_ingredient = None
):
	return True;

def beautifully (
	measured_ingredients = [],
	for_each = for_each,
	
	indent = 0,
	parent_measured_ingredient = None,
):
	for measured_ingredient in measured_ingredients:
		found = for_each (
			measured_ingredient, 
			indent = indent,
			parent_measured_ingredient = parent_measured_ingredient
		)
		if (found):
			return measured_ingredient
			
		if ("unites" in measured_ingredient):
			found_ingredient = beautifully (
				measured_ingredients = measured_ingredient ["unites"],
				for_each = for_each,
				
				indent = indent + 1,
				parent_measured_ingredient = measured_ingredient
			)
			if (type (found_ingredient) == dict):
				return found_ingredient;

	return None