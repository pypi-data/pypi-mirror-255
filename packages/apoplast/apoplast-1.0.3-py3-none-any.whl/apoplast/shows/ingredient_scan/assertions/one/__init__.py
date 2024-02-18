
'''
	This is assertions about the ingredients once 1
	food or supp has been added to them.
'''

'''
import apoplast.shows.ingredient_scan.assertions.one as ingredient_assertions_one
ingredient_assertions_one.sweetly (
	land = land
)
'''

import apoplast.shows.ingredient_scan.grove.assertions as make_grove_assertions

def sweetly (land):
	assert (len (land ["natures"]) == 1)
	make_grove_assertions.about (land ["grove"])
