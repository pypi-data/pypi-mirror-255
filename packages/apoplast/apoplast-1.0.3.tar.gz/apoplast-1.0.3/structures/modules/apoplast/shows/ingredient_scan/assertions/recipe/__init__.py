
'''
	This is assertions about an essential nutrients recipe.
'''

'''
import apoplast.shows.ingredient_scan.assertions.recipe as essentials_nutrients_assertions_recipe
essentials_nutrients_assertions_recipe.splendidly (
	essentials_nutrients = land
)
'''

import apoplast.shows.ingredient_scan.grove.assertions as make_grove_assertions
	

def splendidly (essentials_nutrients):
	assert (len (essentials_nutrients ["natures"]) >= 1)
	make_grove_assertions.about (essentials_nutrients ["grove"])

	return;