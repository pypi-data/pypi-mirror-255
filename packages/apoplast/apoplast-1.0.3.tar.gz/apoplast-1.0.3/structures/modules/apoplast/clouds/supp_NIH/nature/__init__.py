
'''
	#
	#	This retrieves a supp's data from the NIH.	
	#
	import apoplast.clouds.supp_NIH.deliveries.one as retrieve_1_supp
	supp_NIH = retrieve_1_supp.find (
		dsld_id,
		api_key
	)

	import apoplast.clouds.supp_NIH.nature as supp_NIH_nature
	nature = supp_NIH_nature.create (supp_NIH)
'''

'''
	Limitations:
		1. The package mass is not always known.
'''

'''
	Differences from food:
		1a. The ingredients are formatted as a grove
			instead of a list.
			
		1b. The measured ingredients need to be shown
			on the supplement screen.
'''

import apoplast.shows.natures.assertions as natures_assertions

import apoplast.clouds.supp_NIH.nature.form.unit as form_unit_calculator
import apoplast.clouds.supp_NIH.nature.form.amount as form_amount_calculator
import apoplast.clouds.supp_NIH.nature.form.serving_size.amount as serving_size_amount_calculator

import apoplast.clouds.supp_NIH.nature.measured_ingredients as measured_ingredients_builder
import apoplast.clouds.supp_NIH.nature.essential_nutrients as calculate_essential_nutrients
import apoplast.clouds.supp_NIH.nature.cautionary_ingredients as calculate_cautionary_ingredients


from fractions import Fraction
import json
import copy

def create (
	supp_NIH,
	return_measured_ingredients_grove = False
):
	identity = {
		"name":	supp_NIH ["fullName"],
		"FDC ID": "",
		"UPC": supp_NIH ["upcSku"],
		"DSLD ID": str (supp_NIH ["id"])
	}

	nature = {
		"kind": "supp",
		"identity": identity,
		"brand": {
			"name":	supp_NIH ["brandName"]
		},
		"measures": {
			"form": {
				"unit": ""
			},
		}
	}
	
	if ("statements" in supp_NIH):
		nature ["statements"] = supp_NIH ["statements"]
	

	assert ("ingredientRows" in supp_NIH)
	assert ("netContents" in supp_NIH)
	assert ("physicalState" in supp_NIH)
	assert ("servingSizes" in supp_NIH)
	net_contents = supp_NIH ["netContents"]	
	physical_state = supp_NIH ["physicalState"]
	serving_sizes = supp_NIH ["servingSizes"]
	servings_per_container = supp_NIH ["servingsPerContainer"]
	ingredientRows = supp_NIH ["ingredientRows"]
	
	form_unit = form_unit_calculator.calc (
		net_contents = net_contents,
		physical_state = physical_state,
		serving_sizes = serving_sizes,
		
		ingredient_rows = ingredientRows
	)
	form_amount = form_amount_calculator.calc (
		net_contents = net_contents,
		form_unit = form_unit
	)
	
	'''
		Every shape listed might already have this
		in the shape data.
	'''
	serving_size_amount = serving_size_amount_calculator.calc (
		net_contents = net_contents,
		serving_sizes = serving_sizes,
		servings_per_container = servings_per_container,
		form_unit = form_unit,
		
		ingredientRows = ingredientRows
	)

	nature ["measures"]["form"]["amount per package"] = form_amount;
	nature ["measures"]["form"]["unit"] = form_unit
	nature ["measures"]["form"]["serving size amount"] = serving_size_amount
	
	'''
		Is the servings per container an estimate,
		and therefore the nutrient amounts are estimates?
	'''
	if (form_unit == "gram"):
		nature ["measures"]["form"]["amount is an estimate"] = "?"
	
		is_an_estimate = Fraction (form_amount) != (
			Fraction (servings_per_container) *
			Fraction (serving_size_amount)
		)
		if (is_an_estimate):
			nature  ["measures"]["form"]["amount is an estimate"] = "yes"
	
	'''
	
	'''
	measured_ingredients_grove = measured_ingredients_builder.build (
		ingredientRows = supp_NIH ["ingredientRows"],
		form = nature ["measures"]["form"]
	)
	if (return_measured_ingredients_grove):
		return measured_ingredients_grove;

	nature ["measured ingredients"] = measured_ingredients_grove;
	nature ["unmeasured ingredients"] = {
		"list": supp_NIH ["otheringredients"] ["ingredients"]
	}

	print (json.dumps (measured_ingredients_grove, indent = 4))

	'''
		From the measured ingredients grove,
		calculate the essential nutrients.
	'''
	nature ["essential nutrients"] = calculate_essential_nutrients.eloquently (
		copy.deepcopy (measured_ingredients_grove),
		identity
	)
	nature ["cautionary ingredients"] = calculate_cautionary_ingredients.eloquently (
		copy.deepcopy (measured_ingredients_grove),
		identity
	)
	
	
	
	
	'''
	
	'''

	natures_assertions.start (nature)
	return nature