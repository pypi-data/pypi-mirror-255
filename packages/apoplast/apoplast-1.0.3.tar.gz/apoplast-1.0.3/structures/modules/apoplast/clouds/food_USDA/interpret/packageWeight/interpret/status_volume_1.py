

'''
	python3 insurance.py "clouds/food_USDA/interpret/packageWeight/interpret/status_1.py"
'''

'''
	Sometimes when multiple values, one of the values is rounded.
		prefer grams or prefer ounces?
'''

import json

import apoplast.clouds.food_USDA.interpret.packageWeight.interpret as interpreter


def check_1 ():	
	proceeds = interpreter.start ("12 fl oz/355 mL")
	calculated = proceeds.calculated;
	listed = proceeds.listed;

	assert (calculated ['liters'] == '71/200')
	assert (calculated ['fluid ounces'] == '19984723346456576/1664840044750517')

def check_2 ():	
	proceeds = interpreter.start ("355 mL")
	calculated = proceeds.calculated;
	listed = proceeds.listed;

	print (calculated)

	assert (calculated ['liters'] == '71/200')
	assert (calculated ['fluid ounces'] == '19984723346456576/1664840044750517')

		
	
checks = {
	"check 1": check_1,
	"check 2": check_2	
}