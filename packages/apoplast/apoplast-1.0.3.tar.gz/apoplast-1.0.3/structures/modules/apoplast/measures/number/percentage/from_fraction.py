

'''
import apoplast.measures.percentage.from_fraction as percentage_from_fraction
percentage_from_fraction.calc ()
'''

from fractions import Fraction
import math

def calc (
	fraction, 
	decimal_len = 3 # math.inf
):
	the_float = float (Fraction (fraction) * 100)
	the_float_string = str (the_float)

	approved = "1234567890."

	for character in the_float_string:
		assert (character in approved)

	if ("." in the_float_string):
		split = the_float_string.split (".")
		
		'''
			if the right of the decimal has more than
			"decimal_len" characters, e.g. 14.2857
		'''
		if (
			len (split [1]) >= (decimal_len + 1)
		):
			next = int (split [1][decimal_len])
			split [1] = split [1] [0:decimal_len]
			
			'''
				round up if the next digit 
				is greater than or equal
				to 5
			'''
			if (next >= 5):
				split [1] = str (int (split [1]) + 1)
		
		while (len (split [1]) < 3):
			split [1] += "0"
	

	return split [0] + "." + split[1] + "%"