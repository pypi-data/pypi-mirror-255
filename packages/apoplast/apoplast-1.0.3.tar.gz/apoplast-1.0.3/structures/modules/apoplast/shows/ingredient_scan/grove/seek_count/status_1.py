




'''
	python3 insurance.py shows/ingredient_scan/grove/seek_count/status_1.py
'''





import json

def check_1 ():
	import pathlib
	from os.path import dirname, join, normpath
	this_directory = pathlib.Path (__file__).parent.resolve ()	

	import apoplast.shows.ingredient_scan.DB.scan.list as ingredients_DB_list_scan
	import apoplast.shows.ingredient_scan.DB.access as access

	static_essentials_DB = access.DB (
		normpath (join (this_directory, "essentials.JSON"))
	)

	import apoplast.shows.ingredient_scan.grove.nurture as grove_nurture
	grove = grove_nurture.beautifully (
		ingredients_DB = static_essentials_DB
	)

	import apoplast.shows.ingredient_scan.grove.seek_count as seek_grove_count
	count = seek_grove_count.beautifully (grove)
	
	assert (count == 45)
	print ("count:", count)
	
checks = {
	'check 1': check_1
}