
'''
#
#	find name
#
import apoplast.shows.ingredient_scan.DB.scan.seek as seek_nutrient
nutrient = seek_nutrient.presently (
	for_each = lambda essential : True if "thiamin" in essential ["names"] else False
)
'''

'''
#
#	find region
#
import apoplast.shows.ingredient_scan.DB.scan.seek as seek_nutrient
nutrient = seek_nutrient.presently (
	for_each = lambda essential : True if essential ["region"] == 1 else False
)
'''

import apoplast.shows.ingredient_scan.DB.scan.list as ingredients_DB_list_scan

def for_each ():
	return False
	
def presently (
	for_each = for_each
):
	essentials = ingredients_DB_list_scan.retrieve ()
	for essential in essentials:
		if (for_each (essential)):
			return essential
	
	return None