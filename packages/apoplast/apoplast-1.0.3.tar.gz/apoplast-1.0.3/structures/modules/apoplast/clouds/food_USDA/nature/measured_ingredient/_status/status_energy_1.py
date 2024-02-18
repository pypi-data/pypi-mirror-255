


'''
	python3 insurance.py clouds/food_USDA/nature/measured_ingredient/_status/status_energy_1.py
'''
import apoplast.clouds.food_USDA.interpret.packageWeight as package_weight
import apoplast.clouds.food_USDA.nature.form as calculate_form
import apoplast.clouds.food_USDA.nature.measured_ingredient as measured_ingredient_builder

import apoplast.clouds.food_USDA.examples as USDA_examples

import json

def check_1 ():
	#servings_per_package = "4.035714285714286"
	
	USDA_food = USDA_examples.retrieve ("branded/walnuts_1882785.JSON")
	mass_and_volume = package_weight.calc (USDA_food)
		
	form = calculate_form.beautifully (
		servingSize = USDA_food ["servingSize"],
		servingSizeUnit = USDA_food ["servingSizeUnit"],
		mass_and_volume = mass_and_volume
	)
	
	'''
		These nutrient levels are actually faked.
		(454/100) * 679 = 25.9234
	'''
	USDA_food_nutrient = {
		"nutrient": {
			"name": "Energy",
			"unitName": "kcal"
		},
		"amount": 679
	}
	USDA_label_nutrient = {
		"value": 1.6
    }

	measured_ingredient = measured_ingredient_builder.build (
		USDA_food_nutrient,
		mass_and_volume,
		form
	)
	
	print ("measured_ingredient", json.dumps (measured_ingredient, indent = 4))

	assert (
		measured_ingredient ["measures"] ["energy"] ["per package"] ["food calories"] ["fraction string"] ==
		"154133/50"
	)
	assert (
		measured_ingredient ["measures"] ["energy"] ["per package"] ["food calories"] ["decimal string"] ==
		"3082.660"
	)
	
	'''
	assert (
		measured_ingredient ["measures"] ["energy"] ["per package"] ["joules"] ["fraction string"] ==
		"322446236/25"
	)
	assert (
		measured_ingredient ["measures"] ["energy"] ["per package"] ["joules"] ["decimal string"] ==
		"12897849.440"
	)
	'''
	
	assert (
		measured_ingredient ["measures"] ["energy"] ["per package"] ["listed"] ==
		[ "3082.660", "kcal" ]
	)

	return;
	
	
checks = {
	'check 1': check_1
}