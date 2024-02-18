
'''
	python3 insurance.py shows/ingredient_scan/land/measures/sums/status/status_1.py
'''

import apoplast.shows.ingredient_scan.land.measures.sums as land_measures_sums
import apoplast.shows.ingredient_scan.land.build as build_ingredient_scan_land

def check_1 ():
	land = build_ingredient_scan_land.eloquently ()
	land_measures_sums.calc (
		land = land
	)

	return;
	
	
checks = {
	'check 1': check_1 
}