




from fractions import Fraction

def calc (
	form,
	USDA_food_nutrient
):
	food_nutrient_multiplier = form ["servings"] ["calculated"] ["foodNutrient per package multiplier"]
	
	'''
		This could thusly unlist the nutrient.
	'''
	assert ("amount" in USDA_food_nutrient)
	#if ("amount" not in USDA_food_nutrient):
	#	return "?"
		
	
	food_nutrient_amount = USDA_food_nutrient ["amount"]
	
	form_unit = form ["unit"]
	if (form_unit in [ "gram", "liter" ]):
		return Fraction (food_nutrient_amount) * Fraction (food_nutrient_multiplier)
	
	else:
		raise Exception (f"The form provided, '{ form }', was not accounted for.")