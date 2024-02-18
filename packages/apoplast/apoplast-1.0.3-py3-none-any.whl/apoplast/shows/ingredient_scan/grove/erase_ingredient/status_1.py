
'''
	python3 insurance.py shows/ingredient_scan/grove/erase_ingredient/status_1.py
'''

import apoplast.shows.ingredient_scan.grove.nurture as grove_nurture
import apoplast.shows.ingredient_scan.grove.erase_ingredient as grove_erase_ingredient
		
def check_1 ():
	grove = grove_nurture.beautifully ()	
	grove_erase_ingredient.beautifully (
		grove = grove,
		name = "energy"
	)
	
	import apoplast.shows.ingredient_scan.grove.seek_name_or_accepts as grove_seek_name_or_accepts
	energy = grove_seek_name_or_accepts.politely (
		grove = grove,
		name_or_accepts = "energy",
		return_none_if_not_found = True
	)
	assert (energy == None)
	
checks = {
	'check 1': check_1
}