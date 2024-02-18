
'''
import apoplast.measures.number.decimal.reduce as reduce_decimal
decimal_string = reduce_decimal.start (Fraction (1, 3), partial_size = 3)

# 0.333
'''

from fractions import Fraction
import math

import numpy

'''
	89.487
		48, 7
		7 >= 5 -> return 48 + 1

	89.49
'''
def round (integer, smaller_amount_integer):
	if (smaller_amount_integer >= 5):
		return integer + 1

	return integer;

def make_right_side_equal_to_partial_size (partial_size_designated, partial):
	last_index_of_partial = partial_size_designated - 1
	while (len (partial) <= last_index_of_partial):		
		partial = partial + "0"

	return partial

'''
	return_type:
		1	->	"0.000"
		
		#
		#	[1] is whether or not it was rounded
		#
		2	-> 	[ "0.000", False ]
'''
def start (
	fraction, 
	
	partial_size = 3,
	
	round = round
):
	'''
		the partial size currently needs to be equal or greater
		than 1.
	'''
	assert (partial_size >= 1)

	the_float = numpy.format_float_positional (Fraction (fraction))
	#the_float = float (Fraction (fraction).limit_denominator ())
	the_float_string = str (the_float)
	

	'''
		Make sure the float string has only
		the approved characters.
	'''
	approved = "1234567890.-"
	for character in the_float_string:
		assert (character in approved), fraction

	if ("." not in the_float_string):
		print ("the_float_string:", the_float_string)
		raise Exception ("A '.' was not found in the fraction float string '{ the_float_string }'.")

	split = the_float_string.split (".")		
	split [1] = make_right_side_equal_to_partial_size (
		partial_size,
		split [1]
	)
	
	'''
		if the right of the decimal has more than
		"partial_size" characters, e.g. 14.2857
		
		len (2857) >= 3
		
	'''
	if (
		len (split [1]) >= (partial_size + 1)
	):
		smaller_amount_integer = int (split [1][ partial_size ])
		split [1] = int (split [1] [0:partial_size])
		split [1] = str (
			round (
				split [1],
				smaller_amount_integer
			)
		)
		
					
		'''
			if like 1.99 then 2.00
		'''
		if (len (split [1]) > partial_size):
			split [0] = str (int (split[0]) + 1)
			split [1] = split[1][1:]


		'''
			round up if the next digit 
			is greater than or equal
			to 5
		'''
		#if (next >= 5):
		#	split [1] = str (int (split [1]) + 1)		
		#print (split[0], split[1])
	
	
	last_index_of_partial = partial_size - 1
	while (len (split [1]) <= last_index_of_partial):		
		split [1] = "0" + split[1]

	return split [0] + "." + split[1]
	
