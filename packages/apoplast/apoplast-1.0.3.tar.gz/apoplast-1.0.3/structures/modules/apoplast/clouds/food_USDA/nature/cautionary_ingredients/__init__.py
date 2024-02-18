

'''

'''

#
#	ingredient_scan: land
#
import apoplast.shows.ingredient_scan.land.add_measured_ingredient as add_measured_ingredient
import apoplast.shows.ingredient_scan.land.build as build_ingredients_land
import apoplast.shows.ingredient_scan.land.measures.sums as land_measures_sums
import apoplast.shows.ingredient_scan.land.calculate_portions as calculate_portions
	
#
#	ingredient_scan: grove
#
import apoplast.shows.ingredient_scan.grove.seek as grove_seek
import apoplast.shows.ingredient_scan.grove.seek_count as seek_grove_count
import apoplast.shows.ingredient_scan.grove.has_uniters as has_uniters

#
#	ingredient_scan: assertions
#
import apoplast.shows.ingredient_scan.assertions.one as ingredients_assertions_one

#
#	ingredient_scan: cautions_DB
#
import apoplast.shows.ingredient_scan.DB.path as DB_paths
import apoplast.shows.ingredient_scan.DB.access as access

	
import json	


def eloquently (
	measured_ingredients_list = [],
	identity = {},
	records = 1
):	
	cautions_DB = access.DB (
		path = DB_paths.find (DB = "cautions")
	)	

	land = build_ingredients_land.eloquently (
		ingredients_DB = cautions_DB
	)
	grove = land ["grove"]
	natures = land ["natures"]
		
	natures.append ({
		"amount": "1",
		"identity": identity
	})	
	

	
	'''
		This constructs the grove
	'''
	for measured_ingredient in measured_ingredients_list:	
		if (records >= 1):
			if ("name" in measured_ingredient):
				print ("measured_ingredient:", measured_ingredient ['name'])
			else:
				print ("A name was not found in", measured_ingredient)
		
		'''
			If the ingredient is in the DB,
			this adds the ingredient to the land
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
		
		#assert (added == True), measured_ingredient
		
	'''
		priorities:
			[ ] calculate the essential nutrients sums.
	'''
	land_measures_sums.calc (
		land = land
	)
	
	'''
		After the measure sums have been calculated,
		the portions can be calculated from the sums.
	'''
	calculate_portions.illustriously (
		land = land
	)	
		
	'''
		description:
			This makes sure that the story 2 and above "essentials",
			have a uniter that has "natures".
			
			That is make sure if "added, sugars" is listed,
			that "sugars, total" is listed.
		
		example:
			sugars, total	<- make sure that this exists, if "added sugars" is added.
				added, sugars
	'''
	has_uniters.check (grove)
	
	
	'''
		Calculate how many ingredients the 
	'''
	#grove_should_contain_count = len (measured_ingredients_list) - cautionary_count

	
	'''
		assert:
			grove ingredients >= measured ingredients
			
			>= ????
		
		This asserts that the number of nutrients in 
		the grove is greater than or equal to the number 
		of nutrients in the measured ingredients list.
	'''
	#grove_count = seek_grove_count.beautifully (grove)
	#assert (grove_count >= grove_should_contain_count), [
	#	grove_count,
	#	grove_should_contain_count
	#]
	
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