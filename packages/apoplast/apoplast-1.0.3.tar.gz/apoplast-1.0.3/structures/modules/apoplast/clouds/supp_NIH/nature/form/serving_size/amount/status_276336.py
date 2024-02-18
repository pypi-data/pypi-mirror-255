

'''
	246811
'''


'''
	python3 insurance.py clouds/supp_NIH/nature/form/serving_size/amount/status_276336.py
'''

import apoplast.clouds.supp_NIH.nature.form.serving_size.amount as serving_size_amount_calculator
import apoplast.clouds.supp_NIH.nature.form.unit as form_unit
	
def check_1 ():

	import apoplast.clouds.supp_NIH.nature as supp_NIH_nature
	import apoplast.clouds.supp_NIH.examples as NIH_examples
	supp_1 = NIH_examples.retrieve ("coated tablets/multivitamin_276336.JSON")

	
	net_contents = [
		{
			"order": 1,
			"quantity": 90,
			"unit": "Coated Tablet(s)",
			"display": "90 Coated Tablet(s)"
		}
	];
	serving_sizes = [
		{
			"order": 1,
			"minQuantity": 1,
			"maxQuantity": 1,
			"minDailyServings": 1,
			"maxDailyServings": 1,
			"unit": "Tablet(s)",
			"notes": "",
			"inSFB": True
		}
	];
	
	unit = form_unit.calc (
		net_contents = net_contents,
		physical_state = supp_1 ["physicalState"],
		serving_sizes = serving_sizes,
		ingredient_rows = supp_1 ["ingredientRows"]
	)
	
	servings_per_container = "90";
	
	assert ("Coated Tablet" == unit)
	assert (supp_1 ["netContents"] == net_contents)
	assert (supp_1 ["servingSizes"] == serving_sizes)
	assert (supp_1 ["servingsPerContainer"] == servings_per_container), [
		servings_per_container,
		supp_1 ["servingsPerContainer"]
	]

	serving_size_amount = serving_size_amount_calculator.calc (
		ingredientRows = supp_1 ["ingredientRows"],
		net_contents = net_contents,
		serving_sizes = serving_sizes,
		servings_per_container = servings_per_container,
		form_unit = unit
	)
	
	print ("serving_size_amount:", serving_size_amount)
	assert (serving_size_amount == "1"), serving_size_amount

	return;
	
checks = {
	'check 1': check_1
}
