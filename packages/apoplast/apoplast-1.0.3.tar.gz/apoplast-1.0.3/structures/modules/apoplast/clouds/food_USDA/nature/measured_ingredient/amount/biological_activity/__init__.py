
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
	assert (unit_name.lower () == "iu")

	biological_activity__from_portion = amount_per_package__from_portion
	
	'''
	difference = abs (
		biological_activity__from_portion -
		label_nutrient_amount
	)
	assert (difference <= 1)
	'''
	
	if (records >= 1):
		print ("biological_activity__from_portion:", biological_activity__from_portion)
	

	biological_activity_per_package_in_IU = Fraction (biological_activity__from_portion)
	
	return {
		"biological activity": {
			"per package": {
				"listed": [ 
					reduce_decimal.start (
						biological_activity__from_portion, 
						partial_size = 3
					), 
					unit_name 
				],
				"IU": {
					"decimal string": reduce_decimal.start (
						biological_activity_per_package_in_IU, 
						partial_size = 3
					),
					"fraction string": str (biological_activity_per_package_in_IU)
				}
			}
		}
	}