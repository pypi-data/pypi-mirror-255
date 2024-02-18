
'''
	description:
		This should be for calculating the land measures sum of 1 treasure,
		however the treasure can have multiple packages.
'''


'''
	import apoplast.shows.ingredient_scan.land.measures.sums as land_measures_sums
	land_measures_sums.calc (
		land = land
	)
'''

'''
	import apoplast.shows.ingredient_scan.land.measures.sums as land_measures_sums
	import apoplast.shows.ingredient_scan.land.build as build_ingredient_scan_land
	land = build_ingredient_scan_land.eloquently ()
	land_measures_sums.calc (
		land = land
	)
'''


'''
	priorities:
		[ ] story 1 sums:
				
			each story 1 ingredient is added to these:
				land [
					"measures"
				][
					'mass + mass equivalents'
				][
					'per recipe'
				][
					'grams'
				][
					'fraction string'
				]
					
'''

from fractions import Fraction

def calc (
	land = {},
	records = 0
):
	grove = land ['grove']
	land_measures = land ['measures']
	
	for ingredient in grove:
		if (len (ingredient ["natures"]) == 0):
			continue;
		if (len (ingredient ["natures"]) >= 2):
			raise Exception (f"This def is for calculating the sum of a grove with only 1 treasure (food or supp) added")
		
		number_of_packages = Fraction (
			ingredient ["natures"] [ 0 ] ["amount"]
		)
		#assert (number_of_packages == 1), number_of_packages
	
		ingredient_measures = ingredient ["measures"]
		for measure_name in ingredient_measures:
			ingredient_measure = ingredient_measures [ measure_name ]
	
			if (measure_name in [ "biological activity" ]):
				continue;
			if (measure_name in [ "mass + mass equivalents", "energy" ]):
				if (measure_name == "mass + mass equivalents"):
					unit = "grams"
				elif (measure_name == "biological activity"):
					unit = "IU"
				elif (measure_name == "energy"):
					unit = "food calories"
				else:
					raise Exception ("?")
			else:
				raise Exception (f"Measure: '{ measure_name }' was not accounted for.") 
			
			addend = Fraction (
				ingredient_measure [ "per recipe" ] [ unit ] [ "fraction string" ]
			) * number_of_packages
			
			print ("addend:", float (addend))
			
			'''
				This adds the ingredient amount to the land amount.
			'''
			if (measure_name in land_measures):
				current_land_amount = Fraction (
					land_measures [ measure_name ]["per recipe"][unit]["fraction string"]
				)
				if (records >= 1):
					print ('"recipe" sums:')
					print ('	current:', current_land_amount)
					print ('	addend:', addend)
					print ('	addition:', current_land_amount + addend)
					print ()
				
				land_measures [ measure_name ] ["per recipe"] [ unit ] ["fraction string"] = str (
					current_land_amount +
					addend
				)
			else:
				raise Exception (f"The measure '{ measure_name }' was not accounted for.")
			
	return;