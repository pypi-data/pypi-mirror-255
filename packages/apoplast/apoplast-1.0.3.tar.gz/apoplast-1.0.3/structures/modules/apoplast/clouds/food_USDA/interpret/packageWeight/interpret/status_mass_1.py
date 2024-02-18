

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
	proceeds = interpreter.start ("12 oz")
	calculated = proceeds.calculated;
	listed = proceeds.listed;
	
	print ("calculated:", calculated)
	
	# 12 * 28.349523125 = 340.1942775
	assert (calculated ['grams'] == '23939044084102737/70368744177664')
	assert (calculated ['pounds'] == '3/4')


def check_2 ():
	proceeds = interpreter.start ("12 oz/340 g")	
	calculated = proceeds.calculated;
	listed = proceeds.listed;
	
	assert (calculated ['grams'] == '340')
	assert (calculated ['pounds'] == '5981343255101440/7979681361367579')	
	
	
def check_3 ():	
	proceeds = interpreter.start ("1 g")
	calculated = proceeds.calculated;
	listed = proceeds.listed;

	print (calculated)

	assert (calculated ['grams'] == '1')
	
	#
	#	0.002204622621848776 = 1 / 453.59237
	#
	assert (calculated ['pounds'] == '17592186044416/7979681361367579')	

	return
	
	
checks = {
	"check 1": check_1,
	"check 2": check_2,
	"check 3": check_3
}