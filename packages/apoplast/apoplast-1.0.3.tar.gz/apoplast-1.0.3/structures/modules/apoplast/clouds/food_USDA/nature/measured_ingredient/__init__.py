
'''
	import apoplast.clouds.food_USDA.nature.measured_ingredient as measured_ingredient_builder
	measured_ingredient_builder.build ()
'''

'''
	calculating:
		"mass per package" or "equivalent mass per package"
		
		mass_per_package = nutrient_amount * (100) 
'''

import apoplast.measures._interpret.unit_kind
import apoplast.clouds.food_USDA.nature.measured_ingredient.amount
import apoplast.measures.number.decimal.reduce as reduce_decimal

from fractions import Fraction

'''
	grams or ml:
		https://fdc.nal.usda.gov/fdc-app.html#/food-details/2412474/nutrients
		https://fdc.nal.usda.gov/fdc-app.html#/food-details/1960255/nutrients		
'''

def build (
	USDA_food_nutrient,
	mass_and_volume,
	form,

	USDA_label_nutrient = {},
	records = 1
):
	measured_ingredient = {
		"name": USDA_food_nutrient ["nutrient"] ["name"],
		"measures": {}
	}
	
	'''
		
	'''
	measures = amount.calc (
		USDA_food_nutrient,
		mass_and_volume,
		form,

		USDA_label_nutrient = {},
		records = records
	)
	
	if ("mass + mass equivalents" in measures):
		measured_ingredient ["measures"] ["mass + mass equivalents"] = (
			measures ["mass + mass equivalents"]
		)
	
	if ("biological activity" in measures):
		measured_ingredient ["measures"] ["biological activity"] = (
			measures ["biological activity"]
		)
		
	if ("energy" in measures):
		measured_ingredient ["measures"] ["energy"] = (
			measures ["energy"]
		)

	return measured_ingredient