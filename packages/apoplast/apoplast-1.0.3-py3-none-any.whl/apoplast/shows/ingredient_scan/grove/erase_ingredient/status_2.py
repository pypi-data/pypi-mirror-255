
'''
	python3 insurance.py shows/ingredient_scan/grove/erase_ingredient/status_1.py
'''

import apoplast.shows.ingredient_scan.grove.nurture as grove_nurture
import apoplast.shows.ingredient_scan.grove.erase_ingredient as grove_erase_ingredient
		
def check_1 ():
	grove = grove_nurture.beautifully ()
	
	exception_message = ""
	try:
		grove_erase_ingredient.beautifully (
			grove = grove,
			name = "energyy"
		)
	except Exception as E:
		print (str (E))
		
		exception_message = str (E)
		
	assert (
		exception_message ==
		"A deletion did not occur."
	)
		
		
	
	
	
checks = {
	'check 1': check_1
}