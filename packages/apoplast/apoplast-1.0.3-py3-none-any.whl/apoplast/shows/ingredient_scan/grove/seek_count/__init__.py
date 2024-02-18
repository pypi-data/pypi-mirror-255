

'''
import apoplast.shows.ingredient_scan.grove.seek_count as seek_grove_count
seek_grove_count.beautifully (
	grove
)
'''


import copy

def beautifully (grove):
	essentials_count = 0

	def step_into (unites, story = 1):
		nonlocal essentials_count;
	
		for prototype in unites:
			essentials_count += 1
			
			if (len (prototype ["unites"]) >= 1):
				step_into (
					prototype ["unites"],
					story = story + 1
				)

	step_into (grove)

	return essentials_count