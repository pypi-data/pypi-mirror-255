
'''
	python3 insurance.py clouds/food_USDA/nature/_status/status_1.py
'''

from apoplast.insure.override_print import override_print
import apoplast.insure.equality as equality

import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import apoplast.clouds.food_USDA.examples as USDA_examples
import apoplast.clouds.food_USDA.nature as food_USDA_nature

import apoplast.shows.ingredient_scan.grove.seek_measured_ingredient_name as grove_seek_measured_ingredient_name

import json		
import ships
	
def check_1 ():
	walnuts_1882785 = USDA_examples.retrieve ("branded/walnuts_1882785.JSON")
	assertions_foundational.run (walnuts_1882785)
	
	nature = food_USDA_nature.create (walnuts_1882785)

	equality.check (nature ["identity"]["FDC ID"], "1882785")

	assert (
		nature ["measures"]["form"] ==
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
	), nature ["measures"]["form"]


	equality.check (nature ["measures"]["mass"]["ascertained"], True)
	equality.check (
		nature ["measures"]["mass"]["per package"]["grams"]["fraction string"], 
		"454"
	)
	
	equality.check (nature ["measures"]["volume"]["ascertained"], False)
	
	equality.check (nature ["measures"]["energy"]["ascertained"], True)
	equality.check (
		nature ["measures"]["energy"]["per package"]["food calories"]["fraction string"], 
		"154133/50"
	)
	
	protein = grove_seek_measured_ingredient_name.politely (
		grove = nature ["essential nutrients"]["grove"],
		measured_ingredient_name = "protein"
	)
	
	'''
	"measures": {
        "mass + mass equivalents": {
            "per recipe": {
                "grams": {
                    "fraction string": "456528486851663599/7036874417766400"
                }
            },
            "portion of grove": {
                "fraction string": "32178219337562192000/210338053544551424737"
            }
        }
    }
	'''
	
	assert (
		protein ["measures"] ["mass + mass equivalents"] ["portion of grove"] ["fraction string"] ==
		"32178219337562192000/210338053544551424737"
	)
	
	
	#ships.show ("protein:", protein)
	
	
checks = {
	'check 1': check_1
}