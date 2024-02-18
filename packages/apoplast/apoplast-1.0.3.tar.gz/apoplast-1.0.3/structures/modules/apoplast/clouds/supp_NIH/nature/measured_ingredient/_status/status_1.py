
'''
	python3 insurance.py clouds/supp_NIH/nature/measured_ingredient/_status/status_1.py
'''

import apoplast.clouds.supp_NIH.nature.measured_ingredient as measured_ingredient_builder

import json

def check_1 ():
	measured_ingredient = measured_ingredient_builder.build (
		form = {
            "unit": "gram",
            "amount per package": "454",
            "serving size amount": "12",
            "amount is an estimate": "yes"
        },
		NIH_ingredient = {
			"order": 19,
			"ingredientId": 281043,
			"description": "",
			"notes": "",
			"quantity": [
				{
					"servingSizeOrder": 1,
					"servingSizeQuantity": 12,
					"operator": "=",
					"quantity": 75.7,
					"unit": "mg",
					"dailyValueTargetGroup": [
						{
							"name": "Adults and children 4 or more years of age",
							"operator": "=",
							"percent": 6,
							"footnote": None
						}
					],
					"servingSizeUnit": "Gram(s)"
				}
			],
			"nestedRows": [],
			"name": "Calcium",
			"category": "mineral",
			"ingredientGroup": "Calcium",
			"uniiCode": "SY7Q814VUP",
			"alternateNames": [
				"Ca"
			],
			"forms": []
		}
	)

	#print (json.dumps (measured_ingredient, indent = 4))

	assert (
		measured_ingredient ==
		{
			"name": "Calcium",
			"alternate names": [
				"Ca"
			],
			'listed measure': {'amount': {'fraction string': '15980741802747495/17592186044416', 'decimal string': '908.400'}, 'unit kind': 'mass', 'unit': 'mg', 'operator': '='},
			"measures": {
				"mass + mass equivalents": {
					"per package": {
						"is equivalent": "no",
						'listed operator': '=',
						"listed": [
							"908.400",
							"mg"
						],
						"grams": {
							"decimal string": "0.908",
							"fraction string": "3196148360549499/3518437208883200"
						}
					}
				}
			},
			"unites": []
		}
	), measured_ingredient

	return;
	
	
checks = {
	'check 1': check_1
}