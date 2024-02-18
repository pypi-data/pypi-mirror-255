
'''
	python3 insurance.py clouds/food_USDA/nature/measured_ingredients_list/status_1.py
'''


import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import apoplast.clouds.food_USDA.examples as USDA_examples
import json	
	
import apoplast.clouds.food_USDA.nature as food_USDA_nature
import apoplast.clouds.food_USDA.nature.measured_ingredients_list.seek as mil_seek

import apoplast.insure.equalities as equalities

def check_1 ():
	walnuts_1882785 = USDA_examples.retrieve ("branded/walnuts_1882785.JSON")
	assertions_foundational.run (walnuts_1882785)
	
	measured_ingredients_list = food_USDA_nature.create (
		walnuts_1882785,
		return_measured_ingredients_list = True
	)
	
	import apoplast.clouds.food_USDA.nature.measured_ingredients_list.for_each as mil_for_each

	
	print (json.dumps (measured_ingredients_list, indent = 4))
	
	Potassium = mil_seek.start ("Potassium, K", measured_ingredients_list)
	equalities.check ([
		[
			Potassium ["measures"] ["mass + mass equivalents"]["per package"][
				"grams"
			]["fraction string"],
			"97383/50000"
		],
		[
			Potassium ["measures"] ["mass + mass equivalents"]["per package"][
				"grams"
			]["decimal string"],
			"1.948"
		]
	], effect = "exception")
	
	Energy = mil_seek.start ("Energy", measured_ingredients_list)
	equalities.check ([
		[
			Energy ["measures"] ["energy"]["per package"][
				"food calories"
			]["fraction string"],
			"154133/50"
		],
		[
			Energy ["measures"] ["energy"]["per package"][
				"food calories"
			]["decimal string"],
			"3082.660"
		]
	], effect = "exception")
	
	
	vitamin_d = mil_seek.start ("Vitamin D (D2 + D3), International Units", measured_ingredients_list)
	
	assert (
		vitamin_d == 
		{
			"name": "Vitamin D (D2 + D3), International Units",
			"measures": {
				"biological activity": {
					"per package": {
						"listed": [
							"0.000",
							"IU"
						],
						"IU": {
							"decimal string": "0.000",
							"fraction string": "0"
						}
					}
				}
			}
		}
	
	)
	
	print (Potassium)
	
	
	
checks = {
	'check 1': check_1
}


