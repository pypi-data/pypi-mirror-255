
'''
	python3 insurance.py clouds/food_USDA/nature/_status/status_2.py
'''


import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import apoplast.clouds.food_USDA.examples as USDA_examples
import json	
	
import apoplast.clouds.food_USDA.nature as food_USDA_nature

import apoplast.insure.equality as equality

	
def check_1 ():
	food_data = USDA_examples.retrieve ("branded/Gardein_f'sh_2663758.JSON")
	nature = food_USDA_nature.create (food_data)

	equality.check (nature ["identity"]["FDC ID"], "2663758")

	assert (
		nature ["measures"]["form"] ==
		{
            "unit": "gram",
            "amount": "288",
            "servings": {
                "listed": {
                    "serving size amount": "96",
                    "serving size unit": "GRM"
                },
                "calculated": {
                    "serving size amount": "96",
                    "servings per package": "3",
                    "foodNutrient per package multiplier": "72/25",
                    "labelNutrient per package multiplier": "3"
                }
            }
        }
	)


	equality.check (nature ["measures"]["mass"]["ascertained"], True)
	equality.check (
		nature ["measures"]["mass"]["per package"]["grams"]["fraction string"], 
		"288"
	)
	
	equality.check (nature ["measures"]["volume"]["ascertained"], False)
	
	equality.check (nature ["measures"]["energy"]["ascertained"], True)
	equality.check (
		nature ["measures"]["energy"]["per package"]["food calories"]["fraction string"], 
		"14976/25"
	)
	
	
	
	
checks = {
	'check 1': check_1
}