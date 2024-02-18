



'''
	python3 insurance.py shows/ingredient_scan_recipe/formulate/_status/status_supp/status_1.py
	
'''




import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import apoplast.clouds.food_USDA.examples as USDA_examples	
import apoplast.clouds.food_USDA.nature as food_USDA_nature
import apoplast.insure.equality as equality

import apoplast.shows.ingredient_scan_recipe.formulate as formulate_recipe
import apoplast.shows.ingredient_scan.grove.seek_name_or_accepts as grove_seek_name_or_accepts

import apoplast.clouds.supp_NIH.nature as supp_NIH_nature
import apoplast.clouds.supp_NIH.examples as NIH_examples

from fractions import Fraction
from copy import deepcopy
import json

def find_grams (measures):
	return Fraction (
		measures ["mass + mass equivalents"] ["per recipe"] ["grams"] ["fraction string"]
	)
	

def check_1 ():
	supp_1 = supp_NIH_nature.create (
		NIH_examples.retrieve ("other/chia_seeds_214893.JSON")
	)
	supp_2 = supp_NIH_nature.create (
		NIH_examples.retrieve ("coated tablets/multivitamin_276336.JSON")
	)

	print (json.dumps (supp_1, indent = 4))

	supp_1_1 = deepcopy (supp_1)
	supp_2_1 = deepcopy (supp_2)
	
	supp_1_multiplier = 10
	supp_2_multiplier = 10
	
	recipe = formulate_recipe.adroitly ([
		[ supp_1, supp_1_multiplier ],
		[ supp_2, supp_2_multiplier ]
	])
	
	def add (path, data):
		import pathlib
		from os.path import dirname, join, normpath
		this_directory = pathlib.Path (__file__).parent.resolve ()
		example_path = normpath (join (this_directory, path))
		FP = open (example_path, "w")
		FP.write (data)
		FP.close ()
		
	add ("status_1.JSON", json.dumps (recipe, indent = 4))
	
	#print (json.dumps (recipe, indent = 4))

	
checks = {
	"check 1": check_1
}