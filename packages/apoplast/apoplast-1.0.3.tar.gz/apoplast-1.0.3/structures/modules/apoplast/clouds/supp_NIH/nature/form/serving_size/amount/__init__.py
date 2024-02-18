

'''
import apoplast.clouds.supp_NIH.nature.form.serving_size.amount as serving_size_amount_calculator
serving_size_amount_calculator.calc (
	net_contents = "",
	serving_sizes = "",
	servings_per_container = "",
	form_unit = ""
)
'''

'''
	?
		Maybe, This calculates the number that nutrient amount needs
		to be multiplied by, in order to get the sum of the nutrient
		amount in the package?
'''

import apoplast.measures.number.integer.string_is_integer as string_is_integer
import apoplast.insure.equality as equality

import apoplast.clouds.supp_NIH.interpret.ingredientRows.for_each as for_each_IR	

import apoplast.insure.equalities as equalities

from fractions import Fraction

import traceback

   

def calc (
	net_contents = "",
	serving_sizes = "",
	servings_per_container = "",
	form_unit = "",
	
	ingredientRows = []
):

	servings_per_container = str (Fraction (servings_per_container))

	print (
		"servings_per_container:", 
		servings_per_container
	)
	
	'''
		examples: multivitamin_246811
	'''
	if (
		equalities.check ("unit amount eq check 1", [
			[ form_unit, "gram" ],
			[ len (serving_sizes), 2 ],
			[
				serving_sizes [0] ["minQuantity"], 
				serving_sizes [0] ["maxQuantity"]
			],
			[ 
				serving_sizes [0]["unit"],
				"Gram(s)"
			]
		])
	):
		possible_serving_size_quantity = serving_sizes [0] ["minQuantity"]
	
		try:
			assert (len (ingredientRows) >= 1);
		
			print ("here?")
		
			def action (ingredient, indent, parent_ingredient):					
				assert (len (ingredient ["quantity"]) == 1)
				assert (ingredient ["quantity"][0]["servingSizeUnit"] == "Gram(s)"), ingredient
				assert (
					ingredient ["quantity"][0]["servingSizeQuantity"] ==
					possible_serving_size_quantity
				)
				return True;

			for_each_IR.start (
				ingredient_rows = ingredientRows,
				action = action
			)
		
			return str (Fraction (possible_serving_size_quantity))
		except Exception as E:
			traceback.print_exc ()
			print ("Exception found in unit amount check 1:", E)
			pass;
	
	
	
	

	'''
		examples: chia_seeds_214893
	'''
	if (
		equalities.check ("unit amount eq check 2", [
			[ form_unit, "gram" ],
			[ len (serving_sizes), 1 ],
			[
				serving_sizes [0] ["minQuantity"], 
				serving_sizes [0] ["maxQuantity"]
			]
		])
	):
		return str (Fraction (serving_sizes [0] ["maxQuantity"]))

			

	'''
	
	
	'''
	if (equalities.check ([
		[ len (net_contents), 1 ],
		[ len (serving_sizes), 1 ],
		[
			serving_sizes [0] ["minQuantity"],
			serving_sizes [0] ["maxQuantity"]
		],
		[
			Fraction (
				Fraction (net_contents [0] ["quantity"]),
				Fraction (servings_per_container)
			),
			Fraction (serving_sizes [0] ["maxQuantity"])
		]
	])):
		return str (Fraction (serving_sizes [0] ["maxQuantity"]))
	
	'''
	if (
		len (net_contents) == 1 and
		len (serving_sizes) == 1 and
		string_is_integer.check (servings_per_container) and
		serving_sizes [0] ["minQuantity"] == serving_sizes [0] ["maxQuantity"] and
		net_contents [0] ["quantity"] / int (servings_per_container) == serving_sizes [0] ["maxQuantity"]
	):
		return str (Fraction (serving_sizes [0] ["maxQuantity"]))
	'''	
		
	raise Exception ("The defined serving size of the supplement could not be calculated.")
		

	#
	#	This is necessary for composition calculations,
	#	but recommendations should be determined elsewhere.
	#
	#	if:
	#		len (netContents)  == 1 and
	#
	#		import cyte.integer.STRING_IS_integer as STRING_IS_integer
	#		STRING_IS_integer.CHECK (servingsPerContainer)
	#
	#		len (servingSizes) == 1
	#
	#		servingSizes [0].minQuantity == servingSizes[0].maxQuantity
	#
	#		netContents [0].quantity / int (servingsPerContainer) == servingSizes[0].maxQuantity
	#
	#	then:
	#		"quantity" = servingSizes[0].maxQuantity
	#		"quantity" = 3
	#
	


	return;