

import apoplast.clouds.food_USDA.nature.measured_ingredient as measured_ingredient_builder

def build (
	foodNutrients = [],
	mass_and_volume = {},
	form = {},
	
	records = 0
):
	measured_ingredients_list = []

	for USDA_food_nutrient in foodNutrients:
		measured_ingredient = measured_ingredient_builder.build (
			USDA_food_nutrient,
			mass_and_volume,
			form,
			
			records = 0
		)
	
		measured_ingredients_list.append (measured_ingredient)

	
	return measured_ingredients_list