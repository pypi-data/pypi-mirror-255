


import copy
from fractions import Fraction
import json

'''
	course 2
'''
import apoplast.shows.ingredient_scan.land.measures.sums as land_measures_sums
import apoplast.shows.ingredient_scan.land.build as build_ingredient_scan_land
def calculate_from_land_sum (land, amount):
	new_land = build_ingredient_scan_land.eloquently ()
	
	new_land ["grove"] = copy.deepcopy (land ["grove"]);
	land_measures_sums.calc (
		land = new_land
	)
	
	'''
	multiply_measures.effortlessly (
		amount = 1,
		measures = new_land ["measures"]
	)
	'''

	return new_land