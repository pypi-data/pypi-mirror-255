




'''
	python3 insurance.py clouds/supp_NIH/nature/form/unit/status_powder_packets_246811.py
'''

import apoplast.clouds.supp_NIH.nature.form.unit as form_unit
import apoplast.clouds.supp_NIH.examples as NIH_examples


def check_1 ():	
	supp_NIH_example = NIH_examples.retrieve ("powder packets/multivitamin_246811.JSON")
	
	unit = form_unit.calc (
		ingredient_rows = supp_NIH_example ["ingredientRows"],
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
		],
		physical_state = {
			"langualCode": "E0162",
			"langualCodeDescription": "Powder"
		},
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
		]
	)
	
	assert (unit == "gram")
	
	return;
	
	
checks = {
	"check 1": check_1
}