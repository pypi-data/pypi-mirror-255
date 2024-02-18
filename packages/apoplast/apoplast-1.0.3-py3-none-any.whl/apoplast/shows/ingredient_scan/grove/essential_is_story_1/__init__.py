
'''
	import apoplast.shows.ingredient_scan.grove.essential_is_story_1 as essential_is_story_1
	story_1_list = essential_is_story_1.generate_list (grove)
	
	is_story_1 = essential_is_story_1.check (story_1_list, name)
'''

def check (
	story_1_list,
	name
):
	name = name.lower ()

	for entry in story_1_list:
		for entry_name in entry:
			if (entry_name.lower () == name):
				return True;
				
	return False
		
def generate_list (grove):
	story_1_list = []
	
	for entry in grove:
		story_1_list.append (entry ["info"]["names"])

	return story_1_list