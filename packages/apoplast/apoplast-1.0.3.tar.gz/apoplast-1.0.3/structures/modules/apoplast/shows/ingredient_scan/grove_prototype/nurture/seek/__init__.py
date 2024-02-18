
'''
	This is necessary for "nurture".
	
	Thus for the sake of sanity, there's
	a copy exclusively for "nuture".
	
	As in this copy shouldn't be used to
	assertain the status of "nurture".
	
	The other copy is for after nurture.
'''

'''
	import apoplast.shows.ingredient_scan.grove_prototype.nurture.seek as grove_seek
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