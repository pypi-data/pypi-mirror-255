




'''
	python3 insurance.py "clouds/food_USDA/nature/form/status_mass_1.py"
'''

import apoplast.clouds.food_USDA.examples as USDA_examples
import apoplast.clouds.food_USDA.interpret.packageWeight as package_weight
import apoplast.clouds.food_USDA.nature.form as calculate_form

import json

def print_dict (dictionary):
	print (json.dumps (dictionary, indent = 4))

def check_1 ():
	walnuts_1882785 = USDA_examples.retrieve ("branded/walnuts_1882785.JSON")
	mass_and_volume = package_weight.calc (walnuts_1882785)
	
	form = calculate_form.beautifully (
		servingSize = walnuts_1882785 ["servingSize"],
		servingSizeUnit = walnuts_1882785 ["servingSizeUnit"],
		mass_and_volume = mass_and_volume
	)
	
	print_dict (form)

	'''
		form ["servings"] ["calculated"] ["foodNutrient per package multiplier"]
	'''
	assert (
		form ==
		{
			"unit": "gram",
			"amount": "454",
			"servings": {
				"listed": {
					"serving size amount": "28",
					"serving size unit": "g"
				},
				"calculated": {
					"serving size amount": "28",
					"servings per package": "227/14",
					"foodNutrient per package multiplier": "227/50",
					"labelNutrient per package multiplier": "227/14"
				}
			}
		}
	)
	
checks = {
	"check 1": check_1
}