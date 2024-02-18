


'''
	python3 insurance.py shows/ingredient_scan/grove/seek_uniter/status_1.py
'''

import json
import apoplast.shows.ingredient_scan.grove.seek_uniter as seek_uniter
import apoplast.shows.ingredient_scan.grove.nurture as grove_nurture

def check_1 ():	
	uniter = seek_uniter.beautifully (
		grove = grove_nurture.beautifully (),
		name = "sugars, added"
	)
	assert ("sugars, total" in uniter ["info"]["names"])
	
	uniter = seek_uniter.beautifully (
		grove = grove_nurture.beautifully (),
		name = "dietary fiber"
	)
	assert ("carbohydrates" in uniter ["info"]["names"])
	
def check_2 ():	
	uniter = seek_uniter.beautifully (
		grove = grove_nurture.beautifully (),
		name = "calcium"
	)
		
	assert (uniter == None)	
	
checks = {
	'check 1': check_1,
	'check 2': check_2	
}