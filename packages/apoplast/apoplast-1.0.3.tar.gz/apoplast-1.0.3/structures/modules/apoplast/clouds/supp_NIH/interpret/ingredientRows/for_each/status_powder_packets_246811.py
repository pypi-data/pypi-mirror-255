







'''
	python3 insurance.py clouds/supp_NIH/nature/ingredientRows/for_each/status_powder_packets_246811.py
'''

import apoplast.clouds.supp_NIH.interpret.ingredientRows.for_each as for_each_IR
import apoplast.clouds.supp_NIH.examples as NIH_examples

def check_1 ():	
	supp_NIH_example = NIH_examples.retrieve ("powder packets/multivitamin_246811.JSON")

	ingredients_count = 0

	def action (ingredient, indent, parent_ingredient):
		nonlocal ingredients_count;
	
		assert (len (ingredient ["quantity"]) == 1)
		assert (ingredient ["quantity"][0]["servingSizeUnit"] == "Gram(s)")
	
		space = " " * (indent * 4)
		#print (space, ingredient ["name"])
		
		ingredients_count += 1
		
		return True;

	for_each_IR.start (
		ingredient_rows = supp_NIH_example ["ingredientRows"],
		action = action
	)
	
	#print ('ingredients_count:', ingredients_count)
	assert (ingredients_count == 59)
	
	
checks = {
	"check 1": check_1
}