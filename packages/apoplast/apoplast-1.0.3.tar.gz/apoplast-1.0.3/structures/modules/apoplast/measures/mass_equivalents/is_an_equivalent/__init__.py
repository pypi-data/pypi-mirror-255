


'''
	check if a unit ends with one of these
'''

'''
import apoplast.measures.mass_equivalents.is_an_equivalent as is_an_equivalent
is_an_equivalent.calc (unit)
'''

'''
	alpha-tocopherol
'''

equivalencies = [
	[ "RAE" ],
	[ "NE" ],
	[ "DFE" ]
]


def string_ends_with (string, ends_with):
	return string.endswith (ends_with)

def calc (unit):
	for equivalency_synonyms in equivalencies:
		for equivalency_synonym in equivalency_synonyms:
			if (unit.endswith (equivalency_synonym)):
				return True;
				
	return False