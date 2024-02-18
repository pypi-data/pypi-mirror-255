
'''
#
#	essentials (actual)
#
import apoplast.shows.ingredient_scan.DB.scan.list as ingredients_DB_list_scan
ingredients_list = ingredients_DB_list_scan.retrieve ()
'''	

'''
#
#	cautionary (actual)
#
import apoplast.shows.ingredient_scan.DB.path as DB_paths
import apoplast.shows.ingredient_scan.DB.access as access
cautions_DB = access.DB (
	path = DB_paths.find (DB = "cautions")
)

import apoplast.shows.ingredient_scan.DB.scan.list as ingredients_DB_list_scan
cautionary_ingredients_list = ingredients_DB_list_scan.retrieve (
	ingredients_DB = cautions_DB
)
'''	

'''
#
#	extra
#
import apoplast.shows.ingredient_scan.DB.scan.list as ingredients_DB_list_scan
import apoplast.shows.ingredient_scan.DB.access as access
ingredients_list = ingredients_DB_list_scan.retrieve (
	ingredients_DB = access.DB ()
)
'''
	
import apoplast.shows.ingredient_scan.DB.access as access

def retrieve (
	ingredients_DB = access.DB ()
):	
	return ingredients_DB.all ()