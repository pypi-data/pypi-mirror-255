

'''

'''

#
#	Essential Nutrients: land
#
import apoplast.shows.ingredient_scan.land.add_measured_ingredient as add_measured_ingredient
import apoplast.shows.ingredient_scan.land.build as build_ingredients_land
import apoplast.shows.ingredient_scan.land.measures.sums as land_measures_sums
import apoplast.shows.ingredient_scan.land.calculate_portions as calculate_portions
import apoplast.shows.ingredient_scan.land.cultivate as cultivate_ingredient_scan_land	
	
#
#	Essential Nutrients: grove
#
import apoplast.shows.ingredient_scan.grove.seek as grove_seek
import apoplast.shows.ingredient_scan.grove.seek_count as seek_grove_count
import apoplast.shows.ingredient_scan.grove.has_uniters as has_uniters

#
#	Essential Nutrients: assertions
#
import apoplast.shows.ingredient_scan.assertions.one as ingredients_assertions_one

	
import json	


def eloquently (
	measured_ingredients_list = [],
	identity = {},
	records = 1
):	
	land = build_ingredients_land.eloquently ()
	grove = land ["grove"]
	natures = land ["natures"]
		
	natures.append ({
		"amount": "1",
		"identity": identity
	})	
	
	def is_cautionary (measured_ingredient):
		cautions = [
			[ "trans fat", "Fatty acids, total trans" ]
		]
		
		for caution in cautions:
			for cautionary_name in caution:
				if (measured_ingredient ['name'] == cautionary_name):
					return True;
	
		return False
	
	cautionary_count = 0
	
	'''
		This constructs the essential nutrients grove
	'''
	for measured_ingredient in measured_ingredients_list:
		if (is_cautionary (measured_ingredient)):
			cautionary_count += 1
			continue;
	
		if (records >= 1):
			if ("name" in measured_ingredient):
				print ("measured_ingredient:", measured_ingredient ['name'])
			else:
				print ("A name was not found in", measured_ingredient)
		
		'''
			If the ingredient is essential,
			this adds the ingredient to the essentials nutrients
		'''
		added = add_measured_ingredient.beautifully (
			#
			#	This is a reference to the land.
			#
			land = land,
			
			amount = 1,
			source = identity,
			measured_ingredient = measured_ingredient
		)
		
		assert (added == True), measured_ingredient
	
	
	cultivate_ingredient_scan_land.eloquently (
		land = land
	)
	
	
	'''
	land_measures_sums.calc (
		land = land
	)
	calculate_portions.illustriously (
		land = land
	)
	has_uniters.check (grove)
	'''
	
	'''
		Calculate how many ingredients the 
	'''
	grove_should_contain_count = len (measured_ingredients_list) - cautionary_count

	
	'''
		assert:
			grove ingredients >= measured ingredients
			
			>= ????
		
		This asserts that the number of nutrients in 
		the grove is greater than or equal to the number 
		of nutrients in the measured ingredients list.
	'''
	grove_count = seek_grove_count.beautifully (grove)
	assert (grove_count >= grove_should_contain_count), [
		grove_count,
		grove_should_contain_count
	]
	
	'''
		priorities:
		
			[ ]	Could or should assert that there are len (measured_ingredients_list)
				number of grove ingredients with 1 "nature".
	'''
		
	
	
	'''
		assertions
	'''
	ingredients_assertions_one.sweetly (
		land = land
	)	
	
	return land;