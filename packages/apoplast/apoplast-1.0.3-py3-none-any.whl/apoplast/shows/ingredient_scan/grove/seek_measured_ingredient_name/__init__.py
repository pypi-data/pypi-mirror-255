


'''
	This is less preferred than using "seek_name_or_accepts".
'''

'''
	This actually just searches for the "name" or "accpets".
'''

'''
	import apoplast.shows.ingredient_scan.grove.seek_measured_ingredient_name as grove_seek_measured_ingredient_name
	protein = grove_seek_measured_ingredient_name.politely (
		grove = grove,
		measured_ingredient_name = "protein"
	)
'''
import apoplast.shows.ingredient_scan.grove.seek as grove_seek

def politely (
	measured_ingredient_name = "",
	grove = [],
	return_none_if_not_found = False
):
	measured_ingredient_name = measured_ingredient_name.lower ()

	checked = []
	def for_each (entry):		
		accepts = []
		if ("accepts" in entry ["info"]):
			accepts = entry ["info"] ["accepts"]
	
		patterns = [
			* entry ["info"] ["names"],
			* accepts
		]	
		
		checked.append (patterns)
			
		for name in patterns:
			if (measured_ingredient_name == name.lower ().strip ()):			
				return True;
			
		return False

	entry = grove_seek.beautifully (
		grove = grove,
		for_each = for_each
	)
	if (type (entry) != dict):
		if (return_none_if_not_found):
			return None;
	
		raise Exception (f'''
			
			The measured ingredient "{ measured_ingredient_name }" was not found.
			
		''')

	return entry