
'''
	python3 insurance.py "clouds/food_USDA/examples/status_1.py"
'''

import apoplast.clouds.food_USDA.deliveries.one.assertions.branded as assertions_branded
import apoplast.clouds.food_USDA.examples as USDA_examples
import json	
	
def check_1 ():
	walnuts_1882785 = USDA_examples.retrieve ("branded/walnuts_1882785.JSON")
	assertions_branded.run (walnuts_1882785)
	
	#print (json.dumps (walnuts_1882785, indent = 4))
	
	
checks = {
	'check 1': check_1
}