



'''
	python3 insurance.py shows/ingredient_scan/DB/scan/list/status_1.py
'''


import apoplast.shows.ingredient_scan.DB.access as access
import apoplast.shows.ingredient_scan.DB.scan.list as ingredients_DB_list_scan


def check_1 ():
	essentials = ingredients_DB_list_scan.retrieve (
		ingredients_DB = access.DB ()
	)
	
	for essential in essentials:
		print ("essential:", essential)
	
	
checks = {
	'check 1': check_1
}