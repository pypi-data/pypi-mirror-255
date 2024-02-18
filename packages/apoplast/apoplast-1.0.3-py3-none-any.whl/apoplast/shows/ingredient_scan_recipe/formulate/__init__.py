



'''
	import apoplast.shows.ingredient_scan_recipe.formulate as formulate_recipe
	essential_nutrients_recipe = formulate_recipe.adroitly ([
		[ nature_1, amount_1 ],
		[ nature_2, amount_2 ]
	])
'''

'''
	description:
		This merges the land measures into the essential_nutrients_recipe measures.
	
	priorities:
		merge the land { ingredient } measures into the essential_nutrients_recipe ingredient measures. 
'''



from .essential_nutrients.formulate import formulate_essential_nutrients


import apoplast.shows.ingredient_scan.DB.path as DB_paths
import apoplast.shows.ingredient_scan.DB.access as access
cautions_DB = access.DB (
	path = DB_paths.find (DB = "cautions")
)

import apoplast.shows.ingredient_scan.land.build as build_ingredient_scan_land
land = build_ingredient_scan_land.eloquently (
	ingredients_DB = cautions_DB
)


def adroitly (natures_with_amounts):
	return {
		'essential nutrients': formulate_essential_nutrients (
			natures_with_amounts,
			land_kind = "essential nutrients"
		),
		'cautionary ingredients': formulate_essential_nutrients (
			natures_with_amounts,
			land_kind = "cautionary ingredients"
		)
	}