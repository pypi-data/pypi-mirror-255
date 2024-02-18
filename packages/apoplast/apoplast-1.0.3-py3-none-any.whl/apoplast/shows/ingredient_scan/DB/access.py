



'''
	priorities, plan:
		
		This should be for accessing the list of essential 
		nutrients, and the nutrients that they are comprised of.
		
		There could be another access point (like a rethinkdb weave
		access point) for accessing a network weave.
'''

'''
	#
	#	Accessing the essentials DB:
	#
	import apoplast.shows.ingredient_scan.DB.access as access
	essentials_DB = access.DB ()
'''

'''
	#
	#	Accessing the cautions DB:
	#
	import apoplast.shows.ingredient_scan.DB.path as DB_paths
	import apoplast.shows.ingredient_scan.DB.access as access
	cautions_DB = access.DB (
		path = DB_paths.find (DB = "cautions")
	)
'''

'''
	#
	#	Accessing another DB for consistency purposes, etc.
	#
	import pathlib
	from os.path import dirname, join, normpath
	this_directory = pathlib.Path (__file__).parent.resolve ()	

	import apoplast.shows.ingredient_scan.DB.scan.list as ingredients_DB_list_scan
	import apoplast.shows.ingredient_scan.DB.access as access
	ingredients_DB_list = ingredients_DB_list_scan.retrieve (
		essentials_DB = access.DB (
			normpath (join (this_directory, "essentials.JSON"))
		)
	)
'''

'''
	#
	#	Not sure what this does exactly...
	#

	#
	#	Accessing another DB (replica, etc.):
	#
	import apoplast.shows.ingredient_scan.DB.access as access
	import apoplast.shows.ingredient_scan.DB.path as essentials_DB_path
	essentials_DB = access.DB (
		path = essentials_DB_path.find ()
	)
'''

from tinydb import TinyDB, Query
import apoplast.shows.ingredient_scan.DB.path as essentials_DB_path
	
def DB (
	path = essentials_DB_path.find (),
	sort_keys = True
):
	DB = TinyDB (
		path, 
		sort_keys = sort_keys
	)
	
	return DB;