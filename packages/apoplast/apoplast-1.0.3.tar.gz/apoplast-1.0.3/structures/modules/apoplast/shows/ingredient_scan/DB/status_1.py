
'''
	python3 insurance.py shows/ingredient_scan/DB/status_1.py
'''


import apoplast.shows.ingredient_scan.DB.access as access
	
def check_1 ():
	essentials_DB = access.DB ()
	print ("essentials_DB:", essentials_DB)
	
checks = {
	'check 1': check_1
}