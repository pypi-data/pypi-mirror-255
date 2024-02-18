
'''
	python3 insurance.py clouds/supp_NIH/nature/form/unit/status_gram_1.py
'''

import apoplast.clouds.supp_NIH.nature.form.unit as form_unit

def check_1 ():	
	unit = form_unit.calc (
		net_contents = [
			{
				"order": 1,
				"quantity": 16,
				"unit": "Oz(s)",
				"display": "16 Oz(s)"
			},
			{
				"order": 2,
				"quantity": 454,
				"unit": "Gram(s)",
				"display": "454 Gram(s)"
			}
		],
		physical_state = {
			"langualCode": "E0172",
			"langualCodeDescription": "Other (e.g. tea bag)"
		},
		serving_sizes = [
			{
				"order": 1,
				"minQuantity": 12,
				"maxQuantity": 12,
				"minDailyServings": 1,
				"maxDailyServings": None,
				"unit": "Gram(s)",
				"notes": "(1 Tbsp)(1 scoop)",
				"inSFB": True
			}
		]
	)
	
	assert (unit == "gram")
	
	return;
	
	
checks = {
	"check 1": check_1
}