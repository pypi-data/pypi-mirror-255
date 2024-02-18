
'''
	This is now a mass and equivalents swap.
'''

'''
	https://www.wolframalpha.com/input?i=gram+to+pound
'''

'''
	import apoplast.measures.mass.swap as mass_swap
	mass_swap.start ([ 432, "GRAMS" ], "POUNDS")
'''

from fractions import Fraction 

grams_to_pounds = Fraction (1, Fraction (453.59237))
pounds_to_ounces = 16

conversions = {
	"grams": {
		"pounds": grams_to_pounds,
		"ounces": Fraction (grams_to_pounds, pounds_to_ounces),
		
		"milligrams": Fraction (1000, 1),
		"micrograms": Fraction (1000000, 1)
	},
	"milligrams": {		
		"micrograms": Fraction (1000, 1),
		"grams": Fraction (1, 1000)
	},
	"micrograms": {
		"grams": Fraction (1, 1000000),
		"milligrams": Fraction (1, 1000)
	},
	
	
	#
	#	avroidupois
	#
	"pounds": {
		"ounces": 16,
		"grams": Fraction (453.59237)
	},
	"ounces": {
		"pounds": Fraction (1, 16),
		"grams": Fraction (28.349523125)
	},
	
	#
	#	troy
	#
	"troy pounds": {},
	"troy ounces": {}	
}

#
#	these need to be lowercase currenly
#
def retrieve_groups (
	allow_equivalents = False
):
	groups = [
		[ "grams", "gram(s)", "gram", "g", "grm" ],
		[ "milligrams", "milligram", "mg" ],
		[ "micrograms", "microgram", "mcg", "\u00b5g", "µg" ],

		[ "pounds", "pound", "lbs", "lb" ],
		[ "ounces", "ounce", "oz", "ozs" ],
	]
	
	if (allow_equivalents):
		groups [2].append ("mcg rae")
		groups [2].append ("mcg dfe")
		groups [2].append ("mcg at")
		
		groups [1].append ("mg at")
		groups [1].append ("mg ne")
	
	return groups;
	


def find_unit (to_find, allow_equivalents = False):
	groups = retrieve_groups (allow_equivalents = allow_equivalents)

	for GROUP in groups:		
		for UNIT in GROUP:
			if (UNIT == to_find):
				return GROUP [0]
	
	raise Exception (f"Unit '{ to_find }' was not found.")



def start (from_quantity, to_unit, allow_equivalents = False):
	[ from_amount, from_unit ] = from_quantity;

	from_unit = find_unit (
		from_unit.lower (), 
		allow_equivalents = allow_equivalents
	)
	
	to_unit = find_unit (
		to_unit.lower (), 
		allow_equivalents = allow_equivalents
	)

	if (from_unit == to_unit):
		return from_amount

	assert (from_unit in conversions), { "from_unit": from_unit, "to_unit": to_unit }
	assert (to_unit in conversions [ from_unit ]), { "from_unit": from_unit, "to_unit": to_unit }

	return conversions [ from_unit ] [ to_unit ] * Fraction (from_amount);