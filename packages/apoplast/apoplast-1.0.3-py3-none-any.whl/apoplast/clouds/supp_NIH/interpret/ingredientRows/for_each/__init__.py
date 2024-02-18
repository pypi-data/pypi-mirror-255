
'''
	import apoplast.clouds.supp_NIH.nature.ingredientRows.for_each as for_each_IR

	def action (ingredient):
		print (ingredient ["name"]
		return True;

	for_each_IR.start (
		ingredient_rows = ingredientRows,
		action = action
	)
'''

'''
	maybe this works?

	import apoplast.clouds.supp_NIH.nature.ingredientRows.for_each as for_each_IR


	def action (ingredient, indent):
		print (ingredient ["name"]
		return False;

	ingredient = for_each_IR.start (
		ingredient_rows = ingredientRows,
		action = action
	)
'''


'''
	Description:
		This loops through all the "nestedRows" of the "ingredientRows"
'''

def action (ingredient, indent = 0, parent_ingredient = None):
	return True;

def start (
	ingredient_rows = [],
	action = action,
	
	indent = 0,
	parent_ingredient = None,
):
	for ingredient in ingredient_rows:
		advance = action (
			ingredient, 
			indent = indent,
			parent_ingredient = parent_ingredient
		)
		
		if (not advance):
			return;
			
		if ("nestedRows" in ingredient):
			start (
				ingredient_rows = ingredient ["nestedRows"],
				action = action,
				indent = indent + 1,
				parent_ingredient = ingredient
			)

	return;