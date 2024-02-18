

import json

import apoplast.shows.ingredient_scan.grove.seek as grove_seek
import apoplast.shows.ingredient_scan.grove.nurture as grove_nurture
import apoplast.shows.ingredient_scan.grove.seek_name_or_accepts as grove_seek_name_or_accepts
import apoplast.shows.ingredient_scan.land.calculate_portions as calculate_portions
import apoplast.shows.ingredient_scan.land.build.measures as build_land_measures
import apoplast.shows.ingredient_scan.land.multiply_amount as multiply_nature_amount
import apoplast.shows.ingredient_scan.measures.merge as merge_measures

import apoplast.shows.ingredient_scan.DB.path as DB_paths
import apoplast.shows.ingredient_scan.DB.access as access

import apoplast.shows.ingredient_scan_recipe.formulate.calculate.grove_mass_and_mass_eq_sum as calc_grove_mass_and_mass_eq_sum

import copy

def formulate_essential_nutrients (
	natures_with_amounts,
	land_kind = ""
):
	if (land_kind == "cautionary ingredients"):		
		cautions_DB = access.DB (
			path = DB_paths.find (DB = "cautions")
		)
		grove = grove_nurture.beautifully (
			ingredients_DB = cautions_DB
		)
		
		formulated_recipe = {
			"natures": [],
			"measures": build_land_measures.quickly (),
			"grove": grove		
		}
		
	elif (land_kind == "essential nutrients"):
		formulated_recipe = {
			"natures": [],
			"measures": build_land_measures.quickly (),
			"grove": grove_nurture.beautifully ()		
		}
		
	else:
		raise Exception (f"Land kind '{ land_kind }' was not accounted for.")
	

	for nature_with_amounts in natures_with_amounts:
		nature_amount = nature_with_amounts [1];
		land = copy.deepcopy (nature_with_amounts [0] [ land_kind ])
		
		land_measures = land ["measures"]
		land_grove = land ["grove"]
		
		formulated_recipe ["natures"].append (
			land ["natures"] [0]
		)
		
		print ("land:", nature_amount)
		
		'''
			This multiplies the land measures 
			and the land grove measures, then
			adds them to the formulated_recipe measures.
		'''
		multiply_nature_amount.smoothly (
			amount = nature_amount,
			land = land
		)
		merge_measures.calc (
			formulated_recipe ["measures"],
			land ["measures"]
		)
		
		'''
			priorities:
				for each in the land grove:
					1. merge the treasure measures into the formulated_recipe ingredient measures
					2. append the treasure nautres to the formulated_recipe ingredient natures
		'''
		def for_each (treasure_ingredient):
			formulated_recipe_grove_ingredient = grove_seek_name_or_accepts.politely (
				grove = formulated_recipe ["grove"],
				name_or_accepts = treasure_ingredient ["info"] ["names"] [0]
			)
			merge_measures.calc (
				formulated_recipe_grove_ingredient ["measures"],
				treasure_ingredient ["measures"]
			)
			
			assert (len (treasure_ingredient ["natures"]) <= 1);
			
			if (len (treasure_ingredient ["natures"]) == 1):
				formulated_recipe_grove_ingredient ["natures"].append (
					treasure_ingredient ["natures"] [0]
				) 
					
			return False		
		
		grove_seek.beautifully (
			grove = land ["grove"],
			for_each = for_each
		)
	
	
	
	
	'''
		
	'''
	calculate_portions.illustriously (
		land = formulated_recipe
	)
	
	'''
		For a second check, could loop through the ingredients
		in the grove to make sure that their ingredient amounts sum
		equals the essential_nutrients_recipe amount sum.
	'''
	'''
	calc_grove_mass_and_mass_eq_sum.charismatically (
		grove = essential_nutrients_recipe ["grove"]
	)
	'''
	
	
	return formulated_recipe