


'''
import apoplast.measures.number.sci_note as sci_note
sci_note_number = sci_note.calc ('9999999')
'''

'''
	This function does not do any rounding.
'''

from fractions import Fraction
import apoplast.measures.number.decimal.reduce as reduce_decimal


'''
	groups:
		-infinity to -1
		
		
		-1 to 0
		
		
		0 to 1				
			.5				0.5e+0
		
		
		1 to infinity 		1e+0
'''
def calc (
	number,
	exponent_multiples = 3
):
	the_fraction = Fraction (number)

	#print ()
	#print ("calculating", the_fraction)

	places = Fraction (10 ** exponent_multiples)

	if (the_fraction == 0):
		return [
			reduce_decimal.start (
				the_fraction, 
				round = lambda integer, smaller_amount_integer : integer 
			),
			f"e+0"
		]

	
	negative = False
	if (the_fraction < 0):
		the_fraction = abs (the_fraction)
		negative = True
	
		
	#		
	#	1 <= the_fraction <= infinity
	#
	if (the_fraction >= 1):
		divisor = places
		exponent_multiplier = 0
		
		
		'''
			29000 < 1000    -> false -> exponent_multiplier = 1
			29000 < 1000000 -> true
		'''
		while (the_fraction >= divisor):
			exponent_multiplier += 1
			the_fraction = the_fraction / divisor
		
		#print ("	the_fraction:", the_fraction)
		#print ("	decimal:", reduce_decimal.start (the_fraction))
		
		decimal = reduce_decimal.start (
			the_fraction, 
			round = lambda integer, smaller_amount_integer : integer 
		)
		
		if (negative):
			decimal = "-" + decimal;
		
		return [
			decimal,
			f"e+{ str (exponent_multiplier * exponent_multiples) }"
		]
		
	#
	#	0 < the_fraction < 1
	#
	elif (the_fraction > 0 and the_fraction < 1):
		divisor = Fraction (1, places)
		exponent_multiplier = 1
	
		#print ("	divisor:", divisor)
	
		'''
			    1/5 >= 1/1000		-> true -> exponent_multiplier = 1
		'''
		'''
			1/10000 <= 1/1000		-> true -> exponent_multiplier = 1
			   1/10 <= 1/1000       -> false -> exponent_multiplier = 2
		'''
		while (the_fraction < divisor):
			#print (f"{ the_fraction } >= { divisor }")
		
			exponent_multiplier += 1
			the_fraction = places * the_fraction
		
		
		the_fraction = places * the_fraction
		
		decimal = reduce_decimal.start (
			the_fraction, 
			round = lambda integer, smaller_amount_integer : integer  
		)	
		if (negative):
			decimal = "-" + decimal;
			
			
		return [
			decimal,
			f"e-{ str (exponent_multiplier * exponent_multiples) }"
		]



	

	
	





#
