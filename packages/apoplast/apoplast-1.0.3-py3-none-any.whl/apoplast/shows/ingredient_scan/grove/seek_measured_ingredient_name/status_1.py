

'''
	python3 insurance.py shows/ingredient_scan/grove/seek_measured_ingredient_name/status_1.py
'''
import apoplast.shows.ingredient_scan.grove.seek_measured_ingredient_name as grove_seek_measured_ingredient_name
import apoplast.shows.ingredient_scan.grove.nurture as grove_nurture
	
def check_1 ():
	grove = grove_nurture.beautifully ()	
	protein = grove_seek_measured_ingredient_name.politely (
		grove = grove,
		measured_ingredient_name = "prOteIn"
	)
	assert (type (protein) == dict)
	
	print ("protein:", protein)

	return;
	
	
checks = {
	'check 1': check_1
}