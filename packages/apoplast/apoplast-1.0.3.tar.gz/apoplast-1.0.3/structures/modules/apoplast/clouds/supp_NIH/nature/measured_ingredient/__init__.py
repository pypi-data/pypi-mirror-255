
'''
import apoplast.clouds.supp_NIH.nature.measured_ingredient as measured_ingredient_builder
'''

import json
import apoplast.measures._interpret.unit_kind as unit_kind

from fractions import Fraction

import apoplast.measures.energy.swap as energy_swap
import apoplast.measures.mass.swap as mass_swap
import apoplast.measures.number.decimal.reduce as reduce_decimal

def build (
	form,
	NIH_ingredient
):
	measured_ingredient = {
		"name": NIH_ingredient ["name"],
		"alternate names": NIH_ingredient ["alternateNames"],
		"measures": {},
		"listed measure": {},
		"unites": []
	}

	'''
		This parses and makes assertions about the NIH_ingredient 
	'''
	form_amount_per_package = form ["amount per package"]
	form_serving_size_amount = form ["serving size amount"]

	quantity_details = NIH_ingredient ["quantity"]
	assert (len (quantity_details) == 1);
	assert (
		str (quantity_details [0] ["servingSizeQuantity"]) == str (form_serving_size_amount)
	), (quantity_details [0] ["servingSizeQuantity"], form_serving_size_amount);
	
	unit = quantity_details [0] ["unit"]
	quantity = quantity_details [0] ["quantity"]
	operator = quantity_details [0] ["operator"]
	
	if (operator != "="):
		pass;
	
	if (unit == "NP"):
		# The measurements are not known.
		return measured_ingredient
		
	kind = unit_kind.calc (unit)
	
	listed = (
		Fraction (quantity) *
		Fraction (form_serving_size_amount)
	)
	
	measured_ingredient ["listed measure"] = {
		"amount": {
			"fraction string": str (listed),
			"decimal string": reduce_decimal.start (
								listed, 
								partial_size = 3
							)
		},
		
		
		"unit kind": kind,
		"unit": unit,
		"operator": operator
	}
	
	if (kind in [ "mass", "mass equivalent" ]):
		if (operator == "="):
			mass_plus_mass_eq_per_package_in_grams = Fraction (
				mass_swap.start (
					[ 
						listed, 
						unit 
					], 
					"grams",
					allow_equivalents = True
				)
			)
		else:
			mass_plus_mass_eq_per_package_in_grams = 0
		
		if (kind == "mass equivalent"):
			is_equivalent = "yes"
		else:
			is_equivalent = "no"

		measured_ingredient ["measures"] ["mass + mass equivalents"] = {
			"per package": {
				"is equivalent": is_equivalent,
				"listed operator": operator,
				"listed": [ 
					reduce_decimal.start (
						listed, 
						partial_size = 3
					), 
					unit
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
		
	elif (kind == "energy"):
		if (operator == "="):
			energy_in_food_calories = Fraction (energy_swap.start ([ 
				listed, 
				unit 
			], "food calories"))
		else:
			energy_in_food_calories = 0
		
		measured_ingredient ["measures"] ["energy"] = {
			"per package": {
				"listed operator": operator,
				"listed": [ 
					reduce_decimal.start (
						listed, 
						partial_size = 3
					), 
					unit 
				],
				"food calories": {
					"decimal string": reduce_decimal.start (
						energy_in_food_calories, 
						partial_size = 3
					),
					"fraction string": str (energy_in_food_calories)
				}				
			}
		}
	
	elif (kind == "biological activity"):
		assert (unit.lower () == "iu")

		if (operator == "="):
			biological_activity_in_IU = Fraction (listed)
		else:
			biological_activity_in_IU = 0


		measured_ingredient ["measures"] ["biological activity"] = {
			"per package": {
				"listed operator": operator,
				"listed": [ 
					reduce_decimal.start (
						listed, 
						partial_size = 3
					), 
					unit 
				],
				"IU": {
					"decimal string": reduce_decimal.start (
						biological_activity_in_IU, 
						partial_size = 3
					),
					"fraction string": str (biological_activity_in_IU)
				}
			}
		}
	
	else:
		raise Exception (f"The kind '{ kind }' of the NIH ingredient was not accounted for.")
		
		
	return measured_ingredient