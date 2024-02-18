
'''
	caution: not case sensitive
'''

'''
	import apoplast.measures._interpret.unit_kind as unit_kind
	kind = unit_kind.calc ("ml")
'''

volume_unit_groups = [
	[ "liters", "litres", "l" ],
	[ "milliliters", "millilitres", "ml" ],

	[ "fluid ounces", "fl oz" ]
]

#
#	maybe these are case sensitive?
#
mass_unit_groups = [
	[ "grams", "gram", "g", "grm", "gram(s)" ],
	[ "milligrams", "milligram", "mg" ],
	[ "micrograms", "microgram", "mcg", "\u00b5g", "µg" ],

	[ "pounds", "pound", "lbs", "lb" ],
	[ "ounces", "ounce", "oz", "ozs" ],
]

def build_mass_equivalent_unit_groups ():
	return [
		[ "micrograms", "mcg RAE", "mcg DFE", "mcg AT" ],
		[ "milligrams", "mg RAE", "mg DFE", "mg AT", "mg NE" ]
	]
	
mass_equivalent_unit_groups = build_mass_equivalent_unit_groups ()

energy_unit_groups = [
	[ "kcal", "food calories", "calorie(s)", "joules" ]
]

biological_activity_groups = [
	[ "iu" ]
]

def calc (unit):
	for group in volume_unit_groups:
		for group_unit in group:
			if (unit.lower () == group_unit.lower ()):
				return "volume"

	for group in mass_unit_groups:
		for group_unit in group:
			if (unit.lower () == group_unit.lower ()):
				return "mass"
				
	for group in mass_equivalent_unit_groups:
		for group_unit in group:
			if (unit.lower () == group_unit.lower ()):
				return "mass equivalent"
	
	for group in energy_unit_groups:
		for group_unit in group:
			if (unit.lower () == group_unit.lower ()):
				return "energy"
	
	for group in biological_activity_groups:
		for group_unit in group:
			if (unit.lower () == group_unit.lower ()):
				return "biological activity"
	
	raise Exception (f'The unit "{ unit }" could not be interpretted.')
	return "?"