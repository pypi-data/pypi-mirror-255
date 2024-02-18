


'''
	python3 insurance.py clouds/supp_NIH/nature/form/unit/status_powder_270619.py
'''

import apoplast.clouds.supp_NIH.nature.form.unit as form_unit



def check_1 ():	

	'''
	'''
	unit = form_unit.calc (
		net_contents = [
			{
				"order": 1,
				"quantity": 4,
				"unit": "oz",
				"display": "4 oz"
			},
			{
				"order": 2,
				"quantity": 113,
				"unit": "Gram(s)",
				"display": "113 Gram(s)"
			},
			{
				"order": 3,
				"quantity": 0.25,
				"unit": "Pound(s)",
				"display": "0.25 Pound(s)"
			}
		],
		physical_state = {
			"langualCode": "E0162",
			"langualCodeDescription": "Powder"
		},
		serving_sizes = [
			{
				"order": 1,
				"minQuantity": 1,
				"maxQuantity": 1,
				"minDailyServings": 1,
				"maxDailyServings": 1,
				"unit": "Gram(s)",
				"notes": "1 Scoop",
				"inSFB": True
			}
		]
	)
	
	assert (unit == "gram")
	
	return;
	
	
checks = {
	"check 1": check_1
}