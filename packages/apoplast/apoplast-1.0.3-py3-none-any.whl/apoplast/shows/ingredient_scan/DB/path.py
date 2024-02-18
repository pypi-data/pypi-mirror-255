



'''
	import apoplast.shows.ingredient_scan.DB.path as DB_paths
	path = essentials_DB_path.find ()
'''

'''
	import apoplast.shows.ingredient_scan.DB.path as DB_paths
	cautions_path = essentials_DB_path.find (DB = "cautions")
'''


import pathlib
from os.path import dirname, join, normpath

this_directory = pathlib.Path (__file__).parent.resolve ()

paths = {
	"essentials": normpath (
		join (this_directory, "_bases/essentials/essentials.JSON")
	),
	"cautions": normpath (
		join (this_directory, "_bases/cautions/cautions.JSON")
	)
}

def find (DB = "essentials"):
	return paths [ DB ]




