
'''
	python3 insurance.py clouds/food_USDA/nature/_status/status_2412474.py
'''

from apoplast.insure.override_print import override_print
import apoplast.insure.equality as equality

import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import apoplast.clouds.food_USDA.examples as USDA_examples
import apoplast.clouds.food_USDA.nature as food_USDA_nature

import apoplast.shows.ingredient_scan.grove.seek_name_or_accepts as grove_seek_name_or_accepts

from rich import print_json
	
def check_1 ():
	beet_juice_2412474 = USDA_examples.retrieve ("branded/beet_juice_2412474.JSON")
	assertions_foundational.run (beet_juice_2412474)
	
	nature = food_USDA_nature.create (beet_juice_2412474)
	
	#print_json (data = nature ["essential nutrients"] ["measures"])
	
	def for_each (entry):
		names = entry ["info"] ["names"]
		measures = entry ["measures"]
				
			
		
		if ('biological activity' in measures):
			print (names)
			print ("measures:", measures)	
		
				
		return False		

	import apoplast.shows.ingredient_scan.grove.seek as grove_seek
	protein = grove_seek.beautifully (
		grove = nature ["essential nutrients"] ["grove"],
		for_each = for_each
	)
	
checks = {
	'check 1': check_1
}