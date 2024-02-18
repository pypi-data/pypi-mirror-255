


'''
	python3 insurance.py shows/ingredient_scan/grove/nurture/status_1.py
'''


import apoplast.shows.ingredient_scan.grove.nurture as grove_nurture
import apoplast.shows.ingredient_scan.grove.seek as grove_seek
import apoplast.shows.ingredient_scan.grove.print as print_grove

import json

def check_1 ():
	grove = grove_nurture.beautifully (
	
	)
	
	
	
	print_grove.beautifully (
		grove
	)
	
	protein = grove_seek.beautifully (
		grove = grove,
		for_each = lambda entry : True if "protein" in entry ["info"] ["names"] else False
	)
	assert (type (protein) == dict), protein
	assert ("protein" in protein ["info"] ["names"])
	
	print ("protein:", protein)
	
checks = {
	'check 1': check_1
}