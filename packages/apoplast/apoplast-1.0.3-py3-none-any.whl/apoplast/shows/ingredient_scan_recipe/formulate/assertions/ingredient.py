
'''
	import apoplast.shows.ingredient_scan_recipe.formulate.assertions.ingredient as ingredient_assertion
'''

import apoplast.shows.ingredient_scan.grove.seek_name_or_accepts as grove_seek_name_or_accepts

def find_grams (measures):
	return Fraction (
		measures ["mass + mass equivalents"] ["per recipe"] ["grams"] ["fraction string"]
	)

from fractions import Fraction

def check (
	ingredient,
	
	recipe,
	
	food_1_1,
	food_2_1,
	
	food_1_multiplier,
	food_2_multiplier,
	
	food_1,
	food_2
):
	food_1_ingredient_1 = grove_seek_name_or_accepts.politely (
		grove = food_1_1 ["essential nutrients"] ["grove"],
		name_or_accepts = ingredient
	)
	food_2_ingredient_1 = grove_seek_name_or_accepts.politely (
		grove = food_2_1 ["essential nutrients"] ["grove"],
		name_or_accepts = ingredient
	)
	
	print ("original:")
	print (
		"	food_1s:", 
		(find_grams (food_1_ingredient_1 ["measures"])),
		float (find_grams (food_1_ingredient_1 ["measures"])),
	)
	print (
		"	vegan pizza:", 
		(find_grams (food_2_ingredient_1 ["measures"])),
		float (find_grams (food_2_ingredient_1 ["measures"]))
	)
	
	print ()

	food_1_ingredient = grove_seek_name_or_accepts.politely (
		grove = food_1 ["essential nutrients"] ["grove"],
		name_or_accepts = ingredient
	)
	food_2_ingredient = grove_seek_name_or_accepts.politely (
		grove = food_2 ["essential nutrients"] ["grove"],
		name_or_accepts = ingredient
	)
	recipe_ingredient = grove_seek_name_or_accepts.politely (
		grove = recipe ["essential nutrients"] ["grove"],
		name_or_accepts = ingredient
	)
	
	'''
		starts at:
			food_1s: 5021813355368299589/7036874417766400 713.6425999999999
			vegan pizza: 89531560592125469/2251799813685248 39.760000000000005
	'''	
	'''
		ends with:
			recipe: 7752113592587244929/11258999068426240 688.526
			food_1s: 456528486851663599/70368744177664 6487.66
			vegan pizza: 447657802960627345/562949953421312 795.2
			combined: 4099885697773936137/562949953421312 7282.86
	'''
	print ("recipe amounts:")
	print (
		"	recipe:", 
		find_grams (recipe_ingredient ["measures"]), 
		float (find_grams (recipe_ingredient ["measures"]))
	)
	print (
		"	food_1s:", 
		(find_grams (food_1_ingredient ["measures"])),
		float (find_grams (food_1_ingredient ["measures"])),
		
	)
	print (
		"	vegan pizza:", 
		(find_grams (food_2_ingredient ["measures"])),
		float (find_grams (food_2_ingredient ["measures"]))
	)
	print (
		"	combined:", 
		(
			(find_grams (food_1_ingredient ["measures"])) +
			(find_grams (food_2_ingredient ["measures"]))
		),
		float (
			(find_grams (food_1_ingredient ["measures"])) +
			(find_grams (food_2_ingredient ["measures"]))
		)
	)
	
	assert (
		find_grams (recipe_ingredient ["measures"]) == (
			(find_grams (food_1_ingredient_1 ["measures"]) * food_1_multiplier) +
			(find_grams (food_2_ingredient_1 ["measures"]) * food_2_multiplier)
		)
	)