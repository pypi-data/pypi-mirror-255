
'''
	import apoplast.shows.ingredient_scan.land.cultivate as cultivate_ingredient_scan_land
	cultivate_ingredient_scan_land.eloquently (
		land = land
	)
'''

'''
	Description:
		This should be called after all the ingredients have been added
		to the grove.
'''


#
#	Essential Nutrients: land
#
import apoplast.shows.ingredient_scan.land.measures.sums as land_measures_sums
import apoplast.shows.ingredient_scan.land.calculate_portions as calculate_portions
	
#
#	Essential Nutrients: grove
#
import apoplast.shows.ingredient_scan.grove.seek as grove_seek
import apoplast.shows.ingredient_scan.grove.seek_count as seek_grove_count
import apoplast.shows.ingredient_scan.grove.has_uniters as has_uniters
import apoplast.shows.ingredient_scan.grove.erase_ingredient as grove_erase_ingredient
	

#
#	Essential Nutrients: assertions
#
import apoplast.shows.ingredient_scan.assertions.one as ingredients_assertions_one

def eloquently (
	land = {}
):
	'''
		This calculate the measure sums of the supp
		from the the measures of the supp ingredients.
	'''
	land_measures_sums.calc (
		land = land
	)
	
	'''
		This calculate the fractional amounts
		of ingredient measures.
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
	has_uniters.check (land ["grove"])
	
	ingredients_assertions_one.sweetly (
		land = land
	)