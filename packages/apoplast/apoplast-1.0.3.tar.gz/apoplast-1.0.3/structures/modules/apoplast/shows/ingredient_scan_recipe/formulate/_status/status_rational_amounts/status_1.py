





'''
	python3 insurance.py shows/ingredient_scan_recipe/formulate/_status/status_rational_amounts/status_1.py
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
	def retrieve_supp (supp_path):
		return supp_NIH_nature.create (
			NIH_examples.retrieve (supp_path) 
		)
	
	def retrieve_food (food_path):
		return food_USDA_nature.create (
			USDA_examples.retrieve (food_path)
		)
	
	print (json.dumps (retrieve_food ("branded/beet_juice_2412474.JSON"), indent = 4))
	
	recipe = formulate_recipe.adroitly ([
		[ retrieve_supp ("coated tablets/multivitamin_276336.JSON"), 1.2 ],
		[ retrieve_supp ("other/chia_seeds_214893.JSON"), 1.4 ]
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
	
	assert (len (recipe ["essential nutrients"] ["natures"]) == 6)
	
	'''
		These amounts are calculcated another way.
	'''
	assert (
		recipe ["essential nutrients"] ["measures"] ==
		{
			"mass + mass equivalents": {
				"per recipe": {
					"grams": {
						"fraction string": "3661863958435401439007099/225179981368524800000"
					}
				}
			},
			"energy": {
				"per recipe": {
					"food calories": {
						"fraction string": "438088/5"
					}
				}
			}
		}
	), recipe ["essential nutrients"] ["measures"]

	
checks = {
	"check 1": check_1
}