
'''
	import apoplast.clouds.supp_NIH.nature.form.unit as form_unit
	unit = form_unit.calc (
		net_contents = [],
		physical_state = {},
		serving_sizes = []
	)
'''

'''
	python3 insurance.py "clouds/supp_NIH/nature/form/unit/status*.py"
'''

import apoplast.insure.equalities as equalities
import apoplast.clouds.supp_NIH.interpret.ingredientRows.for_each as for_each_IR	
		
def grams_in_net_contents (net_contents):
	for net_content in net_contents:
		if (net_content ["unit"] == "Gram(s)"):
			return True

	return False

def calc (
	net_contents = "",
	physical_state = "",
	serving_sizes = "",
	ingredient_rows = []
):
	'''
	if (
		physical_state ["langualCodeDescription"] == "Other (e.g. tea bag)" and
		grams_in_net_contents (net_contents) and 
		len (serving_sizes) == 1 and
		serving_sizes [0] ["unit"] == "Gram(s)"
	):
		#
		#	the form is 1 gram
		#
		return "gram"
	'''
	
	'''
		246811
	'''
	if (equalities.check ([
		[ 
			physical_state ["langualCodeDescription"] in [ 
				"Powder"
			], 
			True
		],
		[ grams_in_net_contents (net_contents), True ], 
		[ len (serving_sizes), 2 ],
		[ serving_sizes [0] ["unit"], "Gram(s)" ]
	])):
		try:
			assert (len (ingredient_rows) >= 1);
		
			def action (ingredient, indent, parent_ingredient):
				assert (len (ingredient ["quantity"]) == 1)
				assert (ingredient ["quantity"][0]["servingSizeUnit"] == "Gram(s)")
				return True;

			for_each_IR.start (
				ingredient_rows = ingredient_rows,
				action = action
			)
		
			return "gram"
		except Exception as E:
			print ("Exception found in unit determination:", E)
			pass;
	
	'''
		214893
		270619
	'''
	if (equalities.check ([
		[ 
			physical_state ["langualCodeDescription"] in [ 
				"Powder",
				"Other (e.g. tea bag)"
			], 
			True
		],
		[ grams_in_net_contents (net_contents), True ], 
		[ len (serving_sizes), 1 ],
		[ serving_sizes [0] ["unit"], "Gram(s)" ]
	])):
		return "gram"

	if (
		len (net_contents) == 1 and
		net_contents [0] ["unit"] == "Vegan Cap(s)" and 
		physical_state ["langualCodeDescription"] == "Capsule" and
		len (serving_sizes) == 1 and
		serving_sizes [0] ["unit"] == "Capsule(s)"
	):
		return "Vegan Capsule"

	if (
		len (net_contents) == 1 and
		net_contents [0] ["unit"] == "Tablet(s)" and 
		physical_state ["langualCodeDescription"] == "Tablet or Pill" and
		len (serving_sizes) == 1 and
		serving_sizes [0] ["unit"] == "Tablet(s)"
	):
		return "Tablet"
		
	if (
		len (net_contents) == 1 and
		net_contents [0] ["unit"] == "Coated Tablet(s)" and 
		physical_state ["langualCodeDescription"] == "Tablet or Pill" and
		len (serving_sizes) == 1 and
		serving_sizes [0] ["unit"] == "Tablet(s)"
	):
		try:
			assert (len (ingredient_rows) >= 1);
		
			def action (ingredient, indent, parent_ingredient):
				assert (len (ingredient ["quantity"]) == 1)
				assert (ingredient ["quantity"][0]["servingSizeUnit"] in [ "Tablet(s)", "Coated Tablet(s)" ])
				return True;

			for_each_IR.start (
				ingredient_rows = ingredient_rows,
				action = action
			)
		
			return "Coated Tablet"
		except Exception as E:
			print ("Exception found in unit determination:", E)
			pass;
	
		
		
	raise Exception ("The form unit of the supplement could not be calculated.")