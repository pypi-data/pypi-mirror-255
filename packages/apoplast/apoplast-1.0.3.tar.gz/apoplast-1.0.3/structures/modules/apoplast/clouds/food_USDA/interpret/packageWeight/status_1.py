

'''
	python3 insurance.py "clouds/food_USDA/nature/packageWeight/status_1.py"
'''

import apoplast.clouds.food_USDA.interpret.packageWeight as package_weight
import apoplast.clouds.food_USDA.examples as USDA_examples

def check_1 ():
	walnuts_1882785 = USDA_examples.retrieve ("branded/walnuts_1882785.JSON")
	mass_and_volume = package_weight.calc (walnuts_1882785)
	
	print (mass_and_volume)
	
	assert (mass_and_volume ["mass"]["per package"]["grams"]["fraction string"] == "454")
	assert (mass_and_volume ["mass"]["per package"]["grams"]["decimal string"] == "454.00")	
	
	assert (mass_and_volume ["volume"]["per package"]["liters"]["fraction string"] == "?")
	assert (mass_and_volume ["volume"]["per package"]["liters"]["decimal string"] == "?")

def check_2 ():
	beet_juice_2642759 = USDA_examples.retrieve ("branded/beet_juice_2642759.JSON")
	mass_and_volume = package_weight.calc (beet_juice_2642759)
	
	print ("mass_and_volume:", mass_and_volume)
	
	assert (mass_and_volume ["mass"]["per package"]["grams"]["fraction string"] == "?")
	assert (mass_and_volume ["mass"]["per package"]["grams"]["decimal string"] == "?")	
	
	assert (mass_and_volume ["volume"]["per package"]["liters"]["fraction string"] == "71/200")
	assert (mass_and_volume ["volume"]["per package"]["liters"]["decimal string"] == "0.36")
	
		
	
checks = {
	"check 1": check_1,
	"check 2": check_2	
}