

'''
	Details about this can be found in "apoplast.shows.nature".
'''

'''
	limitations:
		
		1. 	
			The structure of the measured ingredients 
			is not given by the API.
			
			This is different from the NIH API, where the 
			structure of the measured ingredients is
			given.
'''

'''
	#
	#	This retrieves a food's data from USDA.	
	#
	import apoplast.clouds.food_USDA.deliveries.one as retrieve_1_food
	food_USDA = retrieve_1_food.presently ()
	
	#
	#	This parses USDA foods into the nature format.
	#
	#		This should use the shared:
	#			apoplast.shows.natures
	#
	import apoplast.clouds.food_USDA.nature as food_USDA_nature
	nature = food_USDA_nature.create (food_USDA)
'''

'''
	This calculates the "defined" section of the "nature".
	
	Defined has common fields that are shared between 
	foods and supplements.
	
	From these common fields, then the "nature" "calculated"
	section can be calculated.
'''

#
import apoplast.shows.natures.assertions as natures_assertions
#
import apoplast.clouds.food_USDA.interpret.packageWeight as package_weight
import apoplast.clouds.food_USDA.interpret.packageWeight.assertions as package_weight_assertions
#
import apoplast.clouds.food_USDA.nature.cautionary_ingredients as calculate_cautionary_ingredients
import apoplast.clouds.food_USDA.nature.form as recommendation_builder
import apoplast.clouds.food_USDA.nature.measured_ingredients_list as measured_ingredients_list_builder
import apoplast.clouds.food_USDA.nature.measured_ingredients_list.seek as mil_seek
import apoplast.clouds.food_USDA.nature.essential_nutrients as calculate_essential_nutrients
import apoplast.clouds.food_USDA.nature.form as calculate_form
#
import copy
from fractions import Fraction
import json
#

def create (
	food_USDA,
	
	return_measured_ingredients_list = False,
	
	records = 0
):
	include_ounces = False
	include_grams = True

	nature = {
		"kind": "food",
		"identity": {
			"name":	food_USDA ["description"],
			"FDC ID": str (food_USDA ["fdcId"]),
			"UPC": food_USDA ["gtinUpc"],
			"DSLD ID": ""
		},
		"brand": {
			"name":	food_USDA ["brandName"],
			"owner": food_USDA ["brandOwner"]
		},
		"measures": {
			"form": {},
			"energy": {
				"ascertained": False,
				"per package": {}
			}
		}
	}
	
	servingSizeUnit = food_USDA ["servingSizeUnit"]
	
	'''
		treasure exclusive modifications.
	'''
	if (food_USDA ["servingSizeUnit"] == "MLT" and str (food_USDA ["fdcId"]) == "2642759"):
		servingSizeUnit = "mL"
		
		
	'''
		This calculates the mass and or volume
		from the "packageWeight".
		
		Neither of these are necessary
		for the recipe calculations,
		since supplements don't always
		have these.
	'''
	mass_and_volume = package_weight.calc (food_USDA);
	volume = mass_and_volume ["volume"]
	mass = mass_and_volume ["mass"]
	nature ["measures"]["mass"] = mass
	nature ["measures"]["volume"] = volume
	
	
	'''
		{
			"unit": "liter",
			"amount": "473/1000",
			"servings": {
				"listed": {
					"serving size amount": "240",
					"serving size unit": "ml"
				},
				"calculated": {
					"serving size amount": "6/25",
					"servings per package": "473/240"
				}
			}
		}
	'''
	form = calculate_form.beautifully (
		servingSize = food_USDA ["servingSize"], 
		servingSizeUnit = servingSizeUnit, 
		mass_and_volume = mass_and_volume
	)
	nature ["measures"]["form"] = form;	
	servings_per_package = form ["servings"]["calculated"]["servings per package"];
	
	
	
	'''
		This builds the measured ingredients list.
	'''
	assert ("foodNutrients" in food_USDA)
	measured_ingredients_list = measured_ingredients_list_builder.build (
		foodNutrients = food_USDA ["foodNutrients"],
		mass_and_volume = mass_and_volume,
		form = form,
		
		records = 0
	)
	if (return_measured_ingredients_list):
		return measured_ingredients_list
	
	nature ["measured ingredients"] = measured_ingredients_list;
	nature ["unmeasured ingredients"] = {
		"string": food_USDA ["ingredients"]
	}
	
	'''
		Essential Nutrients
	'''
	'''	
		essential nutrients grove steps:
		
			1. build an "essential nutrients grove"
			2. for each nutrient
	'''	
	nature ["essential nutrients"] = calculate_essential_nutrients.eloquently (
		copy.deepcopy (measured_ingredients_list),
		identity = nature ["identity"]
	)
	
	'''
		Cautionary Ingredients
	'''
	nature ["cautionary ingredients"] = calculate_cautionary_ingredients.eloquently (
		copy.deepcopy (measured_ingredients_list),
		identity = nature ["identity"]
	)
	
	
	'''
		Extract the "energy" or "calories" from the measured_ingredients_list
		and "energy" to the "measured" section.
	'''
	energy = mil_seek.start ("energy", measured_ingredients_list)
	assert (type (energy) == dict), energy
	measured_ingredients_list.remove (energy)
	nature ["measures"]["energy"]["ascertained"] = True
	nature ["measures"]["energy"]["per package"] = energy ["measures"]["energy"]["per package"]
	assert (type (nature ["measures"]["energy"]) == dict)	
	
	
	'''
		make the generic assertions about the "nature"
	'''
	natures_assertions.start (nature)
	return nature
	
	
	
	
'''

'''