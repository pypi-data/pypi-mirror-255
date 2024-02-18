



'''
	python3 insurance.py shows/ingredient_scan/grove/seek_name_or_accepts/status_1.py
'''
import apoplast.shows.ingredient_scan.grove.seek_name_or_accepts as grove_seek_name_or_accepts
import apoplast.shows.ingredient_scan.grove.nurture as grove_nurture
	
def check_1 ():
	protein = grove_seek_name_or_accepts.politely (
		grove = grove_nurture.beautifully (),
		name_or_accepts = "prOteIn"
	)
	assert (type (protein) == dict)
	print ("protein:", protein)

	return;
	
	
checks = {
	'check 1': check_1
}