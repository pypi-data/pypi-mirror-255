


'''
	python3 insurance.py clouds/food_USDA/nature/measured_ingredient/status_IU_1.py
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
		
		
		(454/100) * 5.71 = 25.9234
	'''
	USDA_food_nutrient = {
		"nutrient": {
			"name": "Vitamin D (D2 + D3), International Units",
			"unitName": "IU"
		},
		"amount": 5.71
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
		measured_ingredient ["measures"] ["biological activity"] ["per package"] ["IU"] ["fraction string"] ==
		"1459357682252203941/56294995342131200"
	)
	assert (
		measured_ingredient ["measures"] ["biological activity"] ["per package"] ["IU"] ["decimal string"] ==
		"25.923"
	)
	assert (
		measured_ingredient ["measures"] ["biological activity"] ["per package"] ["listed"] ==
		[ "25.923", "IU" ]
	)

	return;
	
	
checks = {
	'check 1': check_1
}