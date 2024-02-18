

'''
	246811
'''


'''
	python3 insurance.py clouds/supp_NIH/nature/form/serving_size/amount/status_246811.py
'''

import apoplast.clouds.supp_NIH.nature.form.serving_size.amount as serving_size_amount_calculator

def check_1 ():

	import apoplast.clouds.supp_NIH.nature as supp_NIH_nature
	import apoplast.clouds.supp_NIH.examples as NIH_examples
	supp_1 = NIH_examples.retrieve ("powder packets/multivitamin_246811.JSON")


	net_contents = [
		{
			"order": 1,
			"quantity": 5.29,
			"unit": "Ounce(s)",
			"display": "5.29 Ounce(s)"
		},
		{
			"order": 2,
			"quantity": 150,
			"unit": "Gram(s)",
			"display": "150 Gram(s)"
		},
		{
			"order": 3,
			"quantity": 30,
			"unit": "Powder Packet(s)",
			"display": "30 Powder Packet(s)"
		}
	];
	
	serving_sizes = [
		{
			"order": 1,
			"minQuantity": 5,
			"maxQuantity": 5,
			"minDailyServings": 1,
			"maxDailyServings": 3,
			"unit": "Gram(s)",
			"notes": "adults; 1 packet",
			"inSFB": True
		},
		{
			"order": 2,
			"minQuantity": 0.25,
			"maxQuantity": 0.25,
			"minDailyServings": 1,
			"maxDailyServings": 1,
			"unit": "Teaspoon(s)",
			"notes": "children (age 6+)"
		}
	];
	
	servings_per_container = "30";
	form_unit = "gram"

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
		form_unit = form_unit
	)
	
	print ("serving_size_amount:", serving_size_amount)
	assert (serving_size_amount == "5"), serving_size_amount

	return;
	
checks = {
	'check 1': check_1
}
