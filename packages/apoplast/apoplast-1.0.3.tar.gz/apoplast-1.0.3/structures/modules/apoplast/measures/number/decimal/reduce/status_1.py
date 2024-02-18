


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

	decimal = reduce_decimal.start (
		Fraction (2, 3),
		partial_size = 3
	)
	assert (decimal == "0.667"), decimal

	decimal = reduce_decimal.start (
		float (".57"),
		partial_size = 1
	)
	assert (decimal == "0.6"), decimal

	decimal = reduce_decimal.start (
		float ("1.999"),
		partial_size = 2
	)
	assert (decimal == "2.00"), decimal

	decimal = reduce_decimal.start (
		float ("1.999"),
		partial_size = 1
	)
	assert (decimal == "2.0"), decimal

	decimal = reduce_decimal.start (
		float ("99.999"),
		partial_size = 1
	)
	assert (decimal == "100.0"), decimal

	print ()
	print ("-----")
	print ()

	decimal = reduce_decimal.start (
		float ('5.0057'),
		partial_size = 3
	)
	assert (decimal == '5.006'), decimal

	decimal = reduce_decimal.start (
		Fraction (2091/1000),
		partial_size = 4
	)
	assert (decimal == '2.0910'), decimal
		
	
	decimal = reduce_decimal.start (
		"1",
		partial_size = 4
	)
	assert (decimal == '1.0000'), decimal
	
		
	return;
	
	
checks = {
	"check 1": check_1
}