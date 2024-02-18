

'''
	import apoplast.shows.ingredient_scan.grove.seek_uniter as seek_uniter
	uniter = seek_uniter.beautifully (
		grove = [],
		name = "sugars, total"
	)
'''

import apoplast.shows.ingredient_scan.grove.seek_name_or_accepts as grove_seek_name_or_accepts

'''
protein = grove_seek_name_or_accepts.politely (
	grove = grove,
	measured_ingredient_name = "protein"
)
'''
import apoplast.shows.ingredient_scan.grove.seek as grove_seek

def beautifully (
	grove = [],
	name = ""
):
	def for_each (entry):
		unites = entry ["unites"]
		for entry in unites:
			names = entry ["info"] ["names"]
							
			for entry_name in names:
				if (name == entry_name.lower ().strip ()):			
					return True;
				
		return False		

	
	return grove_seek.beautifully (
		grove = grove,
		for_each = for_each
	)


