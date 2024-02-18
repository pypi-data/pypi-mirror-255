
'''
	import apoplast.shows.ingredient_scan.grove_prototype.nurture as essentials_grove_nurture
	essentials_grove_nurture.beautifully ()
'''

import apoplast.shows.ingredient_scan.DB.scan.list as essentials_list
import apoplast.shows.ingredient_scan.grove_prototype.nurture.seek as grove_seek
	
import json
import copy

def nutrient ():
	return {
		"info": {},
		"ingredients": [],
		"includes": []
	}

def beautifully (
	records = 0
):
	grove_prototype = []

	ingredients_DB_list = essentials_list.retrieve ()
	ingredients_DB_list.sort (key = lambda essential : essential ["region"])

	ingredients_DB_list_size = len (ingredients_DB_list)

	'''
		Build an index from the list.
	'''
	for essential in ingredients_DB_list:		
		essential ["unites"] = []
		grove_prototype.append (essential)
	

	
	'''
		loop through the ingredients_DB_list,
		and construct the essentials_grove
	'''
	def find_region (list, region):
		for entry in list:		
			if (entry ["region"] == region):
				return entry;
				
			if (len (entry ["unites"]) >= 1):
				found = find_region (entry ["unites"], region)
				if (type (found) == dict):
					return found;
					
		return False
	
	
	def add_inclusions (essential, the_list):
		nonlocal grove_prototype;
	
		for region in essential ["includes"]:
			physical = find_region (grove_prototype, region)
			
			copy_of_physical = copy.deepcopy (physical)
			grove_prototype.remove (physical)
			
			essential ["unites"].append (copy_of_physical)
			
			if (records >= 1):
				print ()
				print ("for:", essential ["names"])
				print ("found:", copy_of_physical ["names"])
	
	def build_grove (the_list):
		for essential in the_list:
			if (len (essential ["includes"]) >= 1):
				add_inclusions (essential, the_list)
				
				
				print ("unites:", essential ["unites"])
				
				
				build_grove (essential ["unites"])
			

	build_grove (grove_prototype)


	return grove_prototype;