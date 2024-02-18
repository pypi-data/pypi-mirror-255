

'''
	import apoplast.shows.natures.assertions as natures_assertions
	natures_assertions.start (nature)
'''

def are_equal (v1, v2):
	try:
		assert (v1 == v2);
	except Exception as E:
		print ("not equal:", v1, v2)
		raise Exception (E)

	return;


import json
def start (nature):
	assert ("measures" in nature)

	#print (json.dumps (nature, indent = 4))
	
	
	

	return;