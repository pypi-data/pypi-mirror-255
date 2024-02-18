


'''
	import apoplast.shows.ingredient_scan.grove.sort as sort_the_grove
	sort_the_grove.charismatically ()
'''

import apoplast.shows.ingredient_scan.grove.seek as grove_seek

def sort_grove (grove):
	'''
		alphabetical sort by first nutrient name
		
		entry 
	'''

	def key_sort (entry):
		return entry ["info"] ["names"] [0].lower ()

	grove.sort (
		key = key_sort
	)

	return


def charismatically (grove):
	sort_grove (grove)

	def for_each (entry):
		unites = entry ["unites"]
		if (len (unites) >= 1):
			sort_grove (unites)
		
		return False
		
	grove_seek.beautifully (
		grove = grove,
		for_each = for_each
	)

	return;