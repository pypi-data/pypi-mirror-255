



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

	space = Fraction (456/1000);
	
	'''
		reconverting it from the decimal to the Fraction
		is going to lead to some floating point approximations.
	'''
	approximation = .0000001;

	selector = -10
	while (selector <= 10):		
		decimals.append (
			reduce_decimal.start (
				Fraction (2091/1000) + selector,
				partial_size = 4
			)
		)
			
		selector += space
	
	#print ()
	#print (decimals)
	
	index = 1
	last_index = len (decimals) - 1
	while (index <= last_index):
		#print (			
		#	Fraction (Fraction (decimals [index - 1]) + space),
		#	Fraction (Fraction (decimals [index]))
		#)

		assert (
			Fraction (Fraction (decimals [index - 1]) + space) -
			Fraction (decimals [index]) <=
			approximation
		)
		
		index += 1
	
	
	
	
checks = {
	"check 1": check_1
}