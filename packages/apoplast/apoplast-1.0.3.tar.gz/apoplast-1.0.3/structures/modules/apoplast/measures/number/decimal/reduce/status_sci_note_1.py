


'''
	python3 insurance.py measures/number/decimal/reduce/status_1.py
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
	decimal = reduce_decimal.start (
		Fraction (1, 3),
		partial_size = 3
	)
	assert (decimal == "0.333"), decimal


	
checks = {
	"check 1": check_1
}