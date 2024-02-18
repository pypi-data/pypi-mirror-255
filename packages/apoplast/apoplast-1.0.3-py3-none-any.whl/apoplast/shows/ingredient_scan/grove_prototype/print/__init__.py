

'''
import apoplast.shows.ingredient_scan.grove_prototype.print as print_grove_prototype
print_grove_prototype.beautifully (
	grove_prototype
)
'''


'''
import apoplast.shows.ingredient_scan.grove_prototype.print as print_grove_prototype
print_grove_prototype.beautifully (
	grove_prototype = [{
		"names": [ "carbohydrates" ],
		"unites": [{
			"names": [ "fiber" ],
			"unites": []
		}]
	}]
)
'''

import copy

def beautifully (grove_prototype):

	print ()
	print ("The grove prototype:")
	print ()

	essentials_count = 0

	def print_this (unites, story = 1):
		nonlocal essentials_count;
	
		for prototype in unites:
			essentials_count += 1
		
			prototype_copy = copy.deepcopy (prototype)
			del prototype_copy ['unites']
			
			#print ("prototype_copy:", prototype_copy)
			
			accepts = []
			if ("accepts" in prototype_copy):
				accepts = prototype_copy ["accepts"]
			
			indent = " " * ((story - 0) * 4)
			print (f'''{ 
				indent 
				}{ 
					prototype_copy ["names"] 
				}{ 
					accepts
				}[ { 
					prototype_copy ["region"] 
				} ]''')
			
			if (len (prototype ["unites"]) >= 1):
				print_this (
					prototype ["unites"],
					story = story + 1
				)

	print_this (grove_prototype)
	print ()
	print ("	essentials count =", essentials_count)
	print ()


	class Proceeds:
		count = ""

	proceeds = Proceeds ();
	proceeds.count = essentials_count

	return proceeds