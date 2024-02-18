

'''
	status_chia_seeds_214893
'''
'''
	python3 insurance.py clouds/supp_NIH/nature/measured_ingredients/_status/status_chia_seeds_214893.py
'''

import apoplast.clouds.supp_NIH.nature as supp_NIH_nature
import apoplast.clouds.supp_NIH.examples as NIH_examples
import apoplast.clouds.supp_NIH.nature.measured_ingredients.seek_name as seek_name

import json

def check_1 ():	
	supp_NIH_example = NIH_examples.retrieve ("other/chia_seeds_214893.JSON")
	measured_ingredients = supp_NIH_nature.create (
		supp_NIH_example,
		return_measured_ingredients_grove = True
	)
	
	#print (json.dumps (measured_ingredients, indent = 4))
	
	measured_ingredient = seek_name.beautifully (
		measured_ingredients,
		name = "Phosphorus"
	)
	
	print (json.dumps (measured_ingredient, indent = 4))
	
	assert (
		measured_ingredient ==
		{
			"name": "Phosphorus",
			"alternate names": [],
			'listed measure': {'amount': {'fraction string': '1368', 'decimal string': '1368.000'}, 'unit kind': 'mass', 'unit': 'mg', 'operator': '='},
			"measures": {
				"mass + mass equivalents": {
					"per package": {
						"is equivalent": "no",
						'listed operator': '=',
						"listed": [
							"1368.000",
							"mg"
						],
						"grams": {
							"decimal string": "1.368",
							"fraction string": "171/125"
						}
					}
				}
			},
			"unites": []
		}
	), measured_ingredient
	
	return;
	
checks = {
	"check 1": check_1
}