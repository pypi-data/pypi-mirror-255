



'''
	python3 insurance.py shows/ingredient_scan_recipe/formulate/_status/status_supp/status_1_supp_1.py
'''


import json

import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import apoplast.clouds.food_USDA.examples as USDA_examples	
import apoplast.clouds.food_USDA.nature as food_USDA_nature
import apoplast.insure.equality as equality

import apoplast.shows.ingredient_scan_recipe.formulate as formulate_recipe
import apoplast.shows.ingredient_scan.grove.seek_name_or_accepts as grove_seek_name_or_accepts

from fractions import Fraction

from copy import deepcopy

def find_grams (measures):
	return Fraction (
		measures ["mass + mass equivalents"] ["per recipe"] ["grams"] ["fraction string"]
	)

import apoplast.clouds.supp_NIH.nature as supp_NIH_nature
import apoplast.clouds.supp_NIH.examples as NIH_examples

import json

	

def check_1 ():
	supp_1 = supp_NIH_nature.create (
		NIH_examples.retrieve ("other/chia_seeds_214893.JSON")
	)
	supp_2 = supp_NIH_nature.create (
		NIH_examples.retrieve ("coated tablets/multivitamin_276336.JSON")
	)
	
	'''
	food_1 = food_USDA_nature.create (
		USDA_examples.retrieve ("branded/walnuts_1882785.JSON")
	) ["essential nutrients"]
	'''

	print (json.dumps (supp_1, indent = 4))


	supp_1_1 = deepcopy (supp_1)
	supp_2_1 = deepcopy (supp_2)
	
	supp_1_multiplier = 10
	supp_2_multiplier = 10
	
	recipe = formulate_recipe.adroitly ([
		[ supp_1, supp_1_multiplier ],
		#[ supp_2_1 ["essential nutrients"], supp_2_multiplier ]
	])
	
	print (json.dumps (recipe, indent = 4))

	
checks = {
	"check 1": check_1
}