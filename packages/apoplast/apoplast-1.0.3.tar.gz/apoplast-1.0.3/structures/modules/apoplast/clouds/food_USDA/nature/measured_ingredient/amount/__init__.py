


'''
	To calculate the labelNutrient amount, 
	the labelNutrient name needs to be 
	equated with the foodNutrient name.
	
		This can probably be done with the
		"(essential) relevant nutrients" show.
'''

import apoplast.measures._interpret.unit_kind as unit_kind

import apoplast.clouds.food_USDA.nature.measured_ingredient.amount.per_package.food_nutrient as food_nutrient_calculator
import apoplast.clouds.food_USDA.nature.measured_ingredient.amount.per_package.label_nutrient as label_nutrient_calculator

import apoplast.clouds.food_USDA.nature.measured_ingredient.amount.mass as mass_calculator
import apoplast.clouds.food_USDA.nature.measured_ingredient.amount.biological_activity as biological_activity_calculator
import apoplast.clouds.food_USDA.nature.measured_ingredient.amount.energy as energy_calculator

from fractions import Fraction

def calc (
	USDA_food_nutrient,
	mass_and_volume,
	form,

	USDA_label_nutrient = {},
	records = 1
):	
	if (
		mass_and_volume ["mass"]["ascertained"] or
		mass_and_volume ["volume"]["ascertained"]
	):	
		amount_per_package__from_portion = food_nutrient_calculator.calc (
			form,
			USDA_food_nutrient
		)
	
		assert ("unitName" in USDA_food_nutrient ["nutrient"])
		unit_name = USDA_food_nutrient ["nutrient"] ["unitName"]
		
		if (unit_kind.calc (unit_name) == "mass"):
			return mass_calculator.calc (
				amount_per_package__from_portion,
				unit_name,
				
				USDA_food_nutrient,
				mass_and_volume,
				
				records
			)
		
			
		elif (unit_kind.calc (unit_name) == "biological activity"):
			return biological_activity_calculator.calc (
				amount_per_package__from_portion,
				unit_name,
				
				USDA_food_nutrient,
				mass_and_volume,
				
				records
			)
			
		elif (unit_kind.calc (unit_name) == "energy"):		
			return energy_calculator.calc (
				amount_per_package__from_portion,
				unit_name,
				
				USDA_food_nutrient,
				mass_and_volume,
				
				records
			)
			
		else:
			raise Exception (f"""
			
				The unit kind of unit '{ unit_name }' was 
				not accounted for.
			
			""")
		
	return {}

