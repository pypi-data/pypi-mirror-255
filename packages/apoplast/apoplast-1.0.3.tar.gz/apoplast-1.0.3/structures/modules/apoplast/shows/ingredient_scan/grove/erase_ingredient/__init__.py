
'''
	import apoplast.shows.ingredient_scan.grove.erase_ingredient as grove_erase_ingredient
	grove_erase_ingredient.beautifully (
		grove = grove,
		name = "energy"
	)
'''

'''
	description:
		This loops through the entire grove,
		unless True is returned.
'''


from rich import print_json

def for_each (entry, search_name):
	names = entry ["info"] ["names"]
	for name in names:
		if (name == search_name):
			return True;
			
	return False	

'''
	# recursive
'''
def beautifully (
	grove,
	name = None,
	story = 1
):
	assert (type (name) == str)
	assert (len (name) >= 1)

	s = 0
	last_index = len (grove) - 1
	
	while s <= last_index:
		entry = grove [s]
	
		if (for_each (entry, name)):
			del grove [s]		
			return True
		
		if (len (entry ["unites"]) >= 1):
			inner_grove = entry ["unites"]
		
			deleted = beautifully (
				inner_grove,
				name = name,
				story = story + 1
			);
			if (deleted == True):
				return True;
	
	
		s += 1
	
	if (story == 1):
		raise Exception ("A deletion did not occur.")
	
	return False