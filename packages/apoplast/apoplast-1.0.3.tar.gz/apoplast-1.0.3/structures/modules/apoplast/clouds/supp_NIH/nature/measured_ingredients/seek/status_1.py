
'''
	python3 insurance.py clouds/supp_NIH/nature/measured_ingredients/seek/status_1.py
'''

import apoplast.clouds.supp_NIH.nature.measured_ingredients.seek as seek
	
def check_1 ():
	measured_ingredients = [
		{
			"name": "carbohydrates"
		},
		{
			"name": "protein"
		}
	]

	def for_each (
		measured_ingredient, 
		indent = 0, 
		parent_measured_ingredient = None
	):
		if (measured_ingredient ["name"] == "carbohydrates"):
			return True
		
		return False;

	found = seek.beautifully (
		measured_ingredients = measured_ingredients,
		for_each = for_each
	)
	
	assert (found ["name"] == "carbohydrates")

	return;
	
	
checks = {
	'check 1': check_1
}