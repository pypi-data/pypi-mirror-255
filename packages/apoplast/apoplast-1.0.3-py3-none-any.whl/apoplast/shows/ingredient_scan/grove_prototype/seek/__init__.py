
'''
	This is necessary for "nurture".
'''

'''
	import apoplast.shows.ingredient_scan.grove_prototype.seek as grove_seek
	essentials_grove_nutrient = grove_seek.beautifully (
		essentials = [{
			"names": [ "carbohydrates" ],
			"unites": [{
				"names": [ "fiber" ],
				"unites": []
			}]
		}],
		for_each = lambda essential : True if 
	)
'''

'''
	# recursive
'''
def beautifully (
	essentials,
	for_each = lambda * p, ** k : None,
	
	story = 1
):
	for essential in essentials:
		if (for_each (essential)):
			return essential
		
		if (len (essential ["unites"]) >= 1):
			essentials = essential ["unites"]
		
			beautifully (
				essentials,
				for_each = for_each,
				story = story + 1
			);
		
		

	return None