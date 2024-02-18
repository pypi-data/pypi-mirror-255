
'''
import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
'''

def run (data):
	assert ("fdcId" in data)	
	
	assert ("description" in data)
	assert ("foodNutrients" in data)

	assert ("packageWeight" in data)

	return;