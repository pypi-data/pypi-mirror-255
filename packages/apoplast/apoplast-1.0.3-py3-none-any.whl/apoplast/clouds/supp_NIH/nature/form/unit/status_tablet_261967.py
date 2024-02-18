


'''
	python3 insurance.py clouds/supp_NIH/nature/form/unit/status_tablet_261967.py
'''

import apoplast.clouds.supp_NIH.nature.form.unit as form_unit

def check_1 ():	
	unit = form_unit.calc (
		net_contents = [{
			"order": 1,
			"quantity": 90,
			"unit": "Tablet(s)",
			"display": "90 Tablet(s)"
		}],
		physical_state = {
			"langualCode": "E0155",
			"langualCodeDescription": "Tablet or Pill"
		},
		serving_sizes = [
			{
				"order": 1,
				"minQuantity": 3,
				"maxQuantity": 3,
				"minDailyServings": 1,
				"maxDailyServings": 1,
				"unit": "Tablet(s)",
				"notes": "",
				"inSFB": True
			}
		]
	)
	
	assert (unit == "Tablet"), unit
	
	return;
	
	
checks = {
	"check 1": check_1
}