
import apoplast.measures._interpret.unit_kind as unit_kind
import apoplast.measures.mass.swap as mass_swap
import apoplast.measures.number.decimal.reduce as reduce_decimal
import apoplast.measures.energy.swap as energy_swap

from fractions import Fraction

def calc (
	amount_per_package__from_portion,
	unit_name,		
			
	USDA_food_nutrient,
	mass_and_volume,
	
	records = 1
):

	mass_plus_mass_eq_per_package__from_portion = amount_per_package__from_portion
	
	if (records >= 1):
		print (
			"mass_plus_mass_eq_per_package__from_portion", 
			mass_plus_mass_eq_per_package__from_portion,
			float (mass_plus_mass_eq_per_package__from_portion)
		)				
	
	
	mass_plus_mass_eq_per_package_in_grams = Fraction (mass_swap.start ([ 
		mass_plus_mass_eq_per_package__from_portion, 
		unit_name 
	], "grams"))
	
	return {
		"mass + mass equivalents": {
			"per package": {
				"listed": [ 
					reduce_decimal.start (
						mass_plus_mass_eq_per_package__from_portion, 
						partial_size = 3
					), 
					unit_name 
				],
				"grams": {
					"decimal string": reduce_decimal.start (
						mass_plus_mass_eq_per_package_in_grams, 
						partial_size = 3
					),
					"fraction string": str (mass_plus_mass_eq_per_package_in_grams)
				}
			}
		}
	}