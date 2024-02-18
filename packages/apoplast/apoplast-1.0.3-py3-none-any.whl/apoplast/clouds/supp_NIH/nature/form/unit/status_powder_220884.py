


'''
	python3 insurance.py clouds/supp_NIH/nature/form/unit/status_powder_220884.py
'''

import apoplast.clouds.supp_NIH.nature.form.unit as form_unit


def check_1 ():	

	'''
	'''
	unit = form_unit.calc (
		net_contents = [
			{
				"order": 1,
				"quantity": 15.2,
				"unit": "Ounce(s)",
				"display": "15.2 Ounce(s)"
			},
			{
				"order": 2,
				"quantity": 430,
				"unit": "Gram(s)",
				"display": "430 Gram(s)"
			}
		],
		physical_state = {
			"langualCode": "E0162",
			"langualCodeDescription": "Powder"
		},
		serving_sizes = [
			{
				"order": 1,
				"minQuantity": 43,
				"maxQuantity": 43,
				"minDailyServings": 1,
				"maxDailyServings": 1,
				"unit": "Gram(s)",
				"notes": "1 scoop",
				"inSFB": True
			}
		]
	)
	
	assert (unit == "gram")
	
	return;
	
	
checks = {
	"check 1": check_1
}