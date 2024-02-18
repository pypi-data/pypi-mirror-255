




'''
	https://www.wolframalpha.com/input?i=gram+to+pound
'''

'''
	import apoplast.measures.energy.swap as energy_swap
	energy_swap.start ([ 1, "food calorie" ], "joules")
'''

from fractions import Fraction 

food_calorie_to_joules = 4184

conversions = {
	"food calories": {
		"joules": 4184
	},
	
	"joules": {
		"food calories": Fraction (1, food_calorie_to_joules)
	}
}

#
#	these need to be lowercase currenly
#
GROUPS = [
	[ "joules", "joule(s)", "joule" ],
	[ "food calories", "food calorie", "kcal", "calorie(s)" ],
]


def find_unit (to_find):
	for GROUP in GROUPS:		
		for UNIT in GROUP:
			if (UNIT == to_find):
				return GROUP [0]
	
	raise Exception (f"Unit '{ to_find }' was not found.")

def start (from_quantity, to_unit):
	[ from_amount, from_unit ] = from_quantity;

	from_unit = find_unit (from_unit.lower ())
	to_unit = find_unit (to_unit.lower ())

	if (from_unit == to_unit):
		return from_amount

	assert (from_unit in conversions), { "from_unit": from_unit, "to_unit": to_unit }
	assert (to_unit in conversions [ from_unit ]), { "from_unit": from_unit, "to_unit": to_unit }

	return conversions [ from_unit ] [ to_unit ] * Fraction (from_amount);