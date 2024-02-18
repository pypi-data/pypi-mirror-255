

'''
	import apoplast.clouds.food_USDA.interpret.packageWeight.interpret as package_weight_interpreter
	package_weight_interpreter.interpret ()
'''

'''
	This utilizes the SI unit if a SI and a US Customary unit is given.
	
	Probably usually, the SI amount != the US Customary amount,
	if both are provided.
'''

unit_legend = {	
	"oz": "ounces",
	"lb": "pounds",
	"lbs": "pounds",

	"kg": "kilograms",
	"g": "grams",
	"mg": "micrograms",
	"mcg": "milligrams",
	
	"fl oz": "fluid ounces",
	"quart": "quart",
	
	"ml": "milliliters",
	"l": "liters"
}

volume_units = [ 
	"fl oz", 
	"quart",
	
	"ml",
	"l"
]

mass_units = [ 
	"oz", 
	"lb", 
	"lbs",
	
	"g", 
	"kg", 
	"mg", 
	"mcg" 
]


'''
	lb -> g
	oz -> g
	g -> g
'''

from fractions import Fraction
import json


import apoplast.measures.mass.swap as mass_swap
import apoplast.measures.volume.swap as volume_swap

import apoplast.clouds.food_USDA.interpret.packageWeight.label_splitter as label_splitter

def start (
	parameters,
	records = 1	
):
	if (type (parameters) != str):
		print ("parameters:", parameters)
		raise Exception ("The parameters were not interpretable.")
		
	listed = {}
	given_quantities = parameters.split ("/")
	if (records >= 1):
		print ()
		print ("given quantities:", given_quantities)
		
		
	volume_is_known = False
	mass_is_known = False
	
	
	for given_quantity in given_quantities:
		[ amount, unit ] = label_splitter.start (given_quantity)
		
		amount = str (Fraction (amount))
		
		if (records >= 1):
			print (f"	given quantity: '{ amount }' '{ unit }'")
		
		assert (unit in unit_legend), f"unit: '{ unit }'"
		
		if (unit in volume_units):
			volume_is_known = True
		elif (unit in mass_units):
			mass_is_known = True;
		else:
			print ("unit:", unit)
			raise Exception ("Unit was not found in volume of mass units.")
		
		parsed_unit = unit_legend [ unit ]
		
		listed [ parsed_unit ] = amount

	if (records >= 1):
		print (f"	mass_is_known: '{ mass_is_known }'")
		print (f"	volume_is_known: '{ volume_is_known }'")
		print (f"	listed: '{ listed }'")

	calculated = {}
	if (mass_is_known):
		'''
			If grams is not in "listed",
			then attempt to find another unit
			that can be swapped into grams.
			
				ounces -> grams
				pounds -> grams
		'''
		if ("grams" in listed):
			calculated [ "grams" ] = listed ["grams"]
			
		else:
			if ("ounces" in listed):
				if (records >= 1):
					print (f"	calculating grams from ounces")
			
				calculated ["grams"] = str (mass_swap.start (
					[ listed ["ounces"], "ounces" ],
					"grams"
				))
				
			elif ("pounds" in listed): 	
				if (records >= 1):
					print (f"	calculating grams from pounds")
			
				calculated ["grams"] = str (mass_swap.start (
					[ listed ["pounds"], "pounds" ],
					"grams"
				))
				
			else:
				raise Exception ("The mass, in grams, per package could not be calculated.")

		assert ("grams" in calculated)
		
		
		'''
			calculate pounds from the calculated grams
			value;
		'''
		calculated ["pounds"] = str (mass_swap.start (
			[ calculated ["grams"], "grams" ],
			"pounds"
		))
		
		assert ("pounds" in calculated)
		
	if (volume_is_known):
		#
		#	plan:
		#		calculate ([ "liters", "fluid ounces" ])
		#
	
		def calculate ():
			return;
		
		if ("liters" in listed):
			calculated ["liters"] = listed ["liters"]
			
		else:
			if ("milliliters" in listed): 
				calculated [ "liters" ] = str (volume_swap.start (
					[ listed [ "milliliters" ], "milliliters" ],
					"liters"
				))
		
			elif ("fluid ounces" in listed):
				calculated [ "liters" ] = str (volume_swap.start (
					[ listed [ "fluid ounces" ], "fluid ounces" ],
					"liters"
				))			
				
			else:
				raise Exception ("'liters' per package could not be calculated.")

		
		assert ('liters' in calculated)
		
		calculated ["fluid ounces"] = str (volume_swap.start (
			[ calculated ["liters"], "liters" ],
			"fluid ounces"
		))

	for unit in calculated:	
		calculated [ unit ] = str (Fraction (calculated [ unit ]))

	class Proceeds:
		calculated = {}
		listed = {}
		
	proceeds = Proceeds ()
	proceeds.calculated = calculated
	proceeds.listed = listed

	return proceeds

