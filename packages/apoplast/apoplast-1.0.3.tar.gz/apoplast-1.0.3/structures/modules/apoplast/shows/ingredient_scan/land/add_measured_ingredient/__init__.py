

'''
	description:
		This adds the ingredient to the grove,
		however it doesn't add to the grove 
		sums.
		
		That step is performed after.
'''

'''
	import apoplast.shows.ingredient_scan.land.build as build_ingredient_scan_land
	land = build_ingredient_scan_land.eloquently ()
'''

'''
	import apoplast.shows.ingredient_scan.land.add_measured_ingredient as add_measured_ingredient
	
	added = add_measured_ingredient.beautifully (
		#
		#	This is a reference to the land.
		#
		land = land,
		
		amount = 10,
		source = {
			"name":	"WALNUTS HALVES & PIECES, WALNUTS",
			"FDC ID": "1882785",
			"UPC": "099482434618",
			"DSLD ID": ""
		},
		measured_ingredient = {
			"name": "Potassium, K",
			"measures": {
				"mass + mass equivalents": {
					"per package": {
						"listed": [
							"1947.660",
							"mg"
						],
						"grams": {
							"decimal string": "1.948",
							"fraction string": "97383/50000"
						}
					}
				}
			}
		}
	)
'''

import copy
from fractions import Fraction
import json

import apoplast.shows.ingredient_scan.grove.seek_measured_ingredient_name as grove_seek_measured_ingredient_name
	

def beautifully (
	land = {},
	
	amount = 1,
	source = {},
	measured_ingredient = {},
	
	return_False_if_not_found = True,
	records = 0
):
	amount = Fraction (amount)
	measured_ingredient_name = measured_ingredient ["name"]
	measured_ingredient_measures = measured_ingredient ["measures"];
	
	grove = land ["grove"]
	land_measures = land ["measures"]
	exclusions = land ["exclusions"]
	
	'''
		This locates the measured ingredient in the grove.
	'''
	grove_ingredient = grove_seek_measured_ingredient_name.politely (
		grove = grove,
		measured_ingredient_name = measured_ingredient_name,
		return_none_if_not_found = True
	)
	if (grove_ingredient == None):
		return False;
	assert (type (grove_ingredient) == dict)
	
	
	'''
		This adds the measured_ingredient to the grove_ingredient
		natures list.
	'''
	grove_ingredient ["natures"].append (copy.deepcopy ({
		"amount": str (Fraction (amount)),
		"source": source,
		"ingredient": {
			"name": measured_ingredient_name
		},
		"measures": measured_ingredient_measures
	}))
	
	if (records >= 1):
		print ('grove ingredient:', grove_ingredient)
	
	
	'''
		This adds the measures of the nutrient
		to the measures of the grove ingredient 
		and grove summary. 
	'''
	essential_nutrient_measures = grove_ingredient ["measures"]

	measured_ingredient_measures = copy.deepcopy (measured_ingredient ["measures"])
	for measure in measured_ingredient_measures:
		if (measure in [ "mass + mass equivalents", "biological activity", "energy" ]):
			if (measure == "mass + mass equivalents"):
				unit = "grams"
			elif (measure == "biological activity"):
				unit = "IU"
			elif (measure == "energy"):
				unit = "food calories"
			else:
				raise Exception ("?")
			
			'''
				This builds the "per recipe" measure
				if it's not already built on the ingredient.
			'''
			if (measure not in essential_nutrient_measures):
				if (records >= 1):
					print (f'"{ measure }" is about to be added.')
			
				essential_nutrient_measures [ measure ] = {
					"per recipe": {
						unit: {
							"fraction string": "0"
						}
					}
				}
			
			
			addend = Fraction (
				measured_ingredient_measures [ measure ]["per package"][ unit ]["fraction string"]
			) * amount;
		
		
			'''
				This adds the ingredient amount to the nutrient amount.
			'''
			current_nutrient_amount = Fraction (essential_nutrient_measures [measure]["per recipe"][unit]["fraction string"])
			if (records >= 1):
				print (f'"{ measured_ingredient_name }" nutrient sums:')
				print ('	current:', current_nutrient_amount)
				print ('	addend:', addend)
				print ('	addition:', current_nutrient_amount + addend)
				print ()
			
			essential_nutrient_measures [ measure ]["per recipe"][unit]["fraction string"] = str (
				current_nutrient_amount +
				addend
			)
			
			
			'''
				This adds the ingredient amount to the land amount.
			'''
			'''
			if (measure in [ "mass + mass equivalents", "energy" ]):
				current_land_amount = Fraction (land_measures [measure]["per recipe"][unit]["fraction string"])
				if (records >= 1):
					print ('"recipe" sums:')
					print ('	current:', current_land_amount)
					print ('	addend:', addend)
					print ('	addition:', current_land_amount + addend)
					print ()
				
				land_measures [measure]["per recipe"][unit]["fraction string"] = str (
					current_land_amount +
					addend
				)
			else:
				raise Exception (f"The measure '{ measure }' was not accounted for.")
			'''
			
			
			
		else:
			raise Exception (f"Measure: '{ measure }' was not accounted for.") 
			
			
	return True;