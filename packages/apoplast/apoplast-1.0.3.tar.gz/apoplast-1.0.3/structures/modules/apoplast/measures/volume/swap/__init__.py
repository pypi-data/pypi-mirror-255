
'''
	utilizes:
		US Customary
		System International
'''


'''
	import apoplast.measures.volume.swap as volume_swap
	volume_swap.start ([ 1, "FL OZ" ], "LITER")
'''

from fractions import Fraction 


grams_to_pounds = Fraction (1, Fraction (453.59237))
pounds_to_ounces = 16

#
#	https://en.wikipedia.org/wiki/Fluid_ounce
#		1 fl oz = 29.5735 millilitres 
#		1 fl oz = 0.0295735 liters
#
#		1 liter = 1 / 0.0295735 fl oz
#

#
#	Fraction (1, (Fraction (29.5735) * Fraction (1, 1000)))
#
fluid_ounces_to_liters = Fraction (29.5735) * Fraction (1, 1000)


conversions = {
	#
	#	1 liter = 33.8140227 US ounce 
	#
	"liters": {
		"fluid ounces": Fraction (1, fluid_ounces_to_liters),
		"milliliters": Fraction (1000, 1)
	},
	
	#
	#	1 mL = 1/1000 L 
	#
	"milliliters": {
		"fluid ounces": Fraction (1, fluid_ounces_to_liters) * Fraction (1, 1000),
		"liters": Fraction (1, 1000)
	},
	
	#
	#	1 fl oz = 1/32 quarts 
	#
	"fluid ounces": {
		"quarts": Fraction (1, 32),
		
		"milliliters": fluid_ounces_to_liters * Fraction (1000, 1),
		"liters": fluid_ounces_to_liters
	},
	
	"quarts": {
		"fluid ounces": 32
	}
}


case_insensitive_groups = [
	[ "liters", "litres", "liter", "l" ],
	[ "milliliters", "millilitres", "millilitre", "ml" ],
	[ "fluid ounces", "fluid ounce", "fl oz" ]
]

#
#	
#
case_sensitive_groups = []

'''
case_sensitive_groups = [
	[ "liters", "L" ],
	[ "milliliters", "mL" ],
]
'''

def find_unit (TO_find):
	LOWER_CASE_UNIT = TO_find.lower ()
	for CASE_INSENSITIVE_GROUP in case_insensitive_groups:		
		for UNIT in CASE_INSENSITIVE_GROUP:
			if (UNIT == LOWER_CASE_UNIT):
				return CASE_INSENSITIVE_GROUP [0]
				
	for CASE_SENSITIVE_GROUP in case_sensitive_groups:		
		for UNIT in CASE_SENSITIVE_GROUP:
			if (UNIT == TO_find):
				return CASE_SENSITIVE_GROUP [0]
	
	raise Exception (f"Unit '{ TO_find }' was not found.")


def start (FROM, TO_UNIT):
	[ FROM_AMOUNT, FROM_UNIT ] = FROM;

	FROM_UNIT = find_unit (FROM_UNIT)
	TO_UNIT = find_unit (TO_UNIT)

	assert FROM_UNIT in conversions, f'"{ FROM_UNIT }" was not found"'
	assert (TO_UNIT in conversions [ FROM_UNIT ]), f'"{ TO_UNIT }" was not found in conversions."'

	return conversions [ FROM_UNIT ] [ TO_UNIT ] * Fraction (FROM_AMOUNT);