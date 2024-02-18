
'''
	import apoplast.clouds.food_USDA.nature.form as calculate_form
	form = calculate_form.beautifully (
		servingSize = USDA_food ["servingSize"],
		servingSizeUnit = USDA_food ["servingSizeUnit"],
		mass_and_volume = mass_and_volume
	)
	servings_per_package = form ["servings"] ["calculated"]["servings per package"];
'''

'''
{
	"unit": "liter",
	
	#
	#	the amount per package
	#
	"amount": "473/1000",
	
	"servings": {
		"listed": {
			"serving size amount": "240",
			"serving size unit": "ml"
		},
		"calculated": {
			"serving size amount": "6/25",
			"servings per package": "473/240",
			
			"foodNutrient per package multiplier": "",
			"labelNutrient per package multiplier": "",
		}
	}
}

'''

import apoplast.measures._interpret.unit_kind as unit_kind
import apoplast.measures.volume.swap as volume_swap
import apoplast.measures.mass.swap as mass_swap


from fractions import Fraction


'''
	foodNutrients:
		foodNutrients are amount per 100g or 0.1 liters (100mL)	
			foodNutrient * multiplier = amount of foodNutrient per package
		
		algorithm:
			dividend = 454
			divisor = 100 # grams
			
			(454 / 100) = 4.54
		
			form ["amount"] / divisor 			
'''
def calculate_foodNutrient_per_package_multiplier_for_mass (grams_per_package):
	divisor = 100	
	return Fraction (
		Fraction (grams_per_package),
		divisor
	)
	
def calculate_foodNutrient_per_package_multiplier_for_volume (liters_per_package):
	#
	#	1 liter (or 100mL)
	#
	divisor = Fraction (1, 10) 	
	return Fraction (
		Fraction (liters_per_package),
		divisor
	)
	

'''
	labelNutrient multiplier = servings_per_package
	
		labelNutrient are the amount per serving
		labelNutrient * multiplier = amount of labelNutrient per package
		
		labelNutrient * servings_per_package = amount of labelNutrient per package
		
'''	
'''
def calculate_labelNutrient_per_package_multiplier_for_mass ():
	return
	
def calculate_labelNutrient_per_package_multiplier_for_volume ():
	return
'''	

		

def beautifully (
	servingSize, 
	servingSizeUnit, 
	mass_and_volume
):
	
		

	kind = unit_kind.calc (servingSizeUnit)
	
	mass = mass_and_volume ["mass"]
	volume = mass_and_volume ["volume"]
	

	proceeds = {
		"unit": "",
		"amount": "",
		
		"servings": {
			"listed": {
				"serving size amount": str (Fraction (servingSize)),
				"serving size unit": servingSizeUnit
			},
			
			"calculated": {
				"serving size amount": "",
				"servings per package": "",
				
				"foodNutrient per package multiplier": "",
				"labelNutrient per package multiplier": "",
			}
		},
	}
	
	unit = ""
	if (kind == "volume"):
		unit = "liter"
		assert (volume ["ascertained"] == True)
	
		serving_size_amount = Fraction (
			volume_swap.start ([ 
				servingSize,
				servingSizeUnit
			], "liter")
		)
		
		proceeds ["unit"] = unit;
		proceeds ["amount"] = volume ["per package"] ["liters"] ["fraction string"];
		proceeds ["servings"] ["calculated"]["foodNutrient per package multiplier"] = str (
			calculate_foodNutrient_per_package_multiplier_for_volume (proceeds ["amount"])
		) 
	
	elif (kind == "mass"):
		unit = "gram"
		assert (mass ["ascertained"] == True)
		
		serving_size_amount = Fraction (
			mass_swap.start ([ 
				servingSize,
				servingSizeUnit
			], "gram")
		)
		
		proceeds ["unit"] = unit;
		proceeds ["amount"] = mass ["per package"] ["grams"] ["fraction string"];
		proceeds ["servings"] ["calculated"]["foodNutrient per package multiplier"] = str (
			calculate_foodNutrient_per_package_multiplier_for_mass (proceeds ["amount"])
		) 
		
		
		
		
	else:
		raise Exception (f"""
	
	Kind '{ kind }' of the serving size unit was not accounted for.
		
		""")
		
		
	servings_per_package = Fraction (
		Fraction (proceeds ["amount"]), 
		serving_size_amount
	)

	proceeds ["servings"] ["calculated"]["serving size amount"] = str (serving_size_amount)
	proceeds ["servings"] ["calculated"]["servings per package"] = str (servings_per_package)
	proceeds ["servings"] ["calculated"]["labelNutrient per package multiplier"] = str (servings_per_package)

	return proceeds