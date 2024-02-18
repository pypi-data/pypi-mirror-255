




'''
import apoplast.insure.equality as equality
equality.check (1, 1)
'''

import json
def check (one, two):
	if (one != two):		
		print ("one:", one)
		print ("two:", two)
		raise Exception (f'An inequality was found.')

	return