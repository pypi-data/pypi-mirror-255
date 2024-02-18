

'''
	#
	#	The essentials
	#
	import apoplast.shows.ingredient_scan.grove.nurture as grove_nurture
	grove = grove_nurture.beautifully ()
'''


'''
	#
	#	The cautions
	#
	import apoplast.shows.ingredient_scan.DB.path as DB_paths
	import apoplast.shows.ingredient_scan.DB.access as access
	cautions_DB = access.DB (
		path = DB_paths.find (DB = "cautions")
	)

	import apoplast.shows.ingredient_scan.grove.nurture as grove_nurture
	grove = grove_nurture.beautifully (
		ingredients_DB = cautions_DB
	)
'''


import apoplast.shows.ingredient_scan.DB.scan.list as ingredients_DB_list_scan
import apoplast.shows.ingredient_scan.DB.access as access

import json
import copy


def nutrient ():
	return {
		"info": {},
		"measures": {},
		"natures": [],
		"unites": []
	}

def beautifully (	
	ingredients_DB = access.DB (),
	records = 0
):
	'''
		Pretty sure that this is a modified list
		from the USDA measured ingredients list... etc.?
	'''
	this_grove = []

	added_to_grove_count = 0

	ingredients_DB_list = ingredients_DB_list_scan.retrieve (
		ingredients_DB = ingredients_DB
	)
	
	
	ingredients_DB_list.sort (key = lambda essential : essential ["region"])
	ingredients_DB_list_size = len (ingredients_DB_list)



	'''
		Add "unites" to each essential.
	'''
	for essential in ingredients_DB_list:		
		this_grove.append ({
			"info": essential,
			"measures": {},
			"natures": [],
			"unites": []
		})
		
	#print_json (data = this_grove)

	'''
		This is a "recursive" loop through 
		the list,
		that constructs this_grove.
	'''
	def find_region (list, region):
		for entry in list:		
			if (entry ["info"] ["region"] == region):
				return entry;
				
			if (len (entry ["unites"]) >= 1):
				found = find_region (entry ["unites"], region)
				if (type (found) == dict):
					return found;
					
		return False
	
	
	'''
	
	'''
	def add_inclusions (entry, the_list):
		nonlocal this_grove;
	
		'''
			This loops through the inclusions
			of a (nature).
			
			If there's a problem here, it probably
			means that the nature that a nature
			points to is now deleted.
			
			for example:
				scene 1:
					nature 43
						includes:
							nature 49
					
				scene 2:
					delete 49
				
				scene 3:
					error can't find 49
		'''
		for region in entry ["info"] ["includes"]:
			physical = find_region (this_grove, region)
			copy_of_physical = copy.deepcopy (physical)
			
			#print (physical, region)
			
			this_grove.remove (physical)
			
			entry ["unites"].append (copy_of_physical)
			
			if (records >= 1):
				print ()
				print ("for:", entry ["info"] ["names"])
				print ("found:", copy_of_physical ["info"] ["names"])
	
	'''
	
	'''
	def build_grove (the_list):
		for entry in the_list:		
			if (len (entry ["info"] ["includes"]) >= 1):
				add_inclusions (entry, the_list)
								
				build_grove (entry ["unites"])
			

	build_grove (this_grove)

	return this_grove