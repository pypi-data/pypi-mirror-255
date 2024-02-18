
'''
	python3 insurance.py clouds/supp_NIH/nature/form/unit/status_vegan_capsule_248267.py
'''

import apoplast.clouds.supp_NIH.nature.form.unit as form_unit

def check_1 ():	
	unit = form_unit.calc (
		net_contents = [
			{
				"order": 1,
				"quantity": 90,
				"unit": "Vegan Cap(s)",
				"display": "90 Vegan Cap(s)"
			}
		],
		physical_state = {
			"langualCode": "E0159",
			"langualCodeDescription": "Capsule"
		},
		serving_sizes = [
			{
				"order": 1,
				"minQuantity": 1,
				"maxQuantity": 1,
				"minDailyServings": 1,
				"maxDailyServings": 3,
				"unit": "Capsule(s)",
				"notes": "",
				"inSFB": True
			}
		]
	)
	
	assert (unit == "Vegan Capsule"), unit
	
	return;
	
	
checks = {
	"check 1": check_1
}