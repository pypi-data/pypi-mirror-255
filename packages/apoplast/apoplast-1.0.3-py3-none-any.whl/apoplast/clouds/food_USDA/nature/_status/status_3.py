
'''
	python3 insurance.py clouds/food_USDA/nature/_status/status_3.py
'''

from apoplast.insure.override_print import override_print
import apoplast.insure.equality as equality

import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import apoplast.clouds.food_USDA.examples as USDA_examples
import apoplast.clouds.food_USDA.nature as food_USDA_nature

import apoplast.shows.ingredient_scan.grove.seek_name_or_accepts as grove_seek_name_or_accepts

from rich import print_json
	
def check_1 ():
	walnuts_1882785 = USDA_examples.retrieve ("branded/walnuts_1882785.JSON")
	assertions_foundational.run (walnuts_1882785)
	
	nature = food_USDA_nature.create (walnuts_1882785)
	equality.check (nature ["identity"]["FDC ID"], "1882785")
	
	print_json (data = nature ["essential nutrients"] ["measures"])
	
	energy = grove_seek_name_or_accepts.politely (
		grove = nature ["essential nutrients"] ["grove"],
		name_or_accepts = "energy",
		
		return_none_if_not_found = True
	)
	
	print_json (data = energy)
	
checks = {
	'check 1': check_1
}