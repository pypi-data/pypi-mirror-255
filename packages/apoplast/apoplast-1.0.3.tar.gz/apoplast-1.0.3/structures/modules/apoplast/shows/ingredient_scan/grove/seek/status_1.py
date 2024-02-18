
'''
	python3 insurance.py shows/ingredient_scan/grove/seek/status_1.py
'''

import apoplast.shows.ingredient_scan.grove.nurture as grove_nurture
import apoplast.shows.ingredient_scan.grove.seek as grove_seek
		
def check_1 ():
	grove = grove_nurture.beautifully ()	

	
	sodium = grove_seek.beautifully (
		grove = grove,
		for_each = (
			lambda entry : True if (
				"sodium, na" in list (map (
					lambda name : name.lower (), 
					entry ["info"] ["names"]
				))
			) else False
		)
	)
	
	assert (type (sodium) == dict)

	return;
	
	
checks = {
	'check 1': check_1
}