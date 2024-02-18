





'''
	python3 status/statuses/vitals/__init__.py numbers/decimal/reduce/status_2.py
'''

'''
	decimals = []

	selector = 1
	while (selector <= 1000):
		decimals.append (Fraction (1/100) + selector)
		selector += 1
'''

import apoplast.measures.number.decimal.reduce as reduce_decimal
from fractions import Fraction

def check_1 ():
	decimals = []

	selector = -10000
	while (selector <= 10000):		
		decimals.append (
			reduce_decimal.start (
				Fraction (1/100) + selector,
				partial_size = 3
			)
		)
			
		selector += 1
	
	index = 1
	last_index = len (decimals) - 1
	while (index <= last_index):
	
		'''
		print (
			decimals [index - 1], 
			decimals [index], 
			Fraction (decimals [index - 1]) + 1,
			Fraction (decimals [index])
		)
		'''
	
		assert (
			Fraction (decimals [index - 1]) + 1 == 
			Fraction (decimals [index])
		)
		
		index += 1
	
	
	
	
checks = {
	"check 1": check_1
}