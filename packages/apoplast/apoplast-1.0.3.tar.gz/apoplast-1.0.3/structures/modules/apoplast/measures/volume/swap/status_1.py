


'''
	python3 insurance.py "measures/volume/swap/status_1.py"
'''

import apoplast.measures.volume.swap as volume_swap

from fractions import Fraction

def check_EQ (ONE, TWO, is_float = False):
	if (ONE != TWO):
		if (is_float == True):
			raise Exception (
				f'{ float (ONE) } != { float (TWO) }'
			)
		
		else:
			raise Exception (
				f'{ ONE } != { TWO }'
			)
		
	return;


def check_1 ():
	#
	#		1 fl oz = 29.5735 millilitres 
	#		1 fl oz = 0.0295735 liters
	#
	#		1 liter = 1 / 0.0295735 fl oz
	#
	check_EQ (
		volume_swap.start ([ 1, "FL OZ" ], "milliliters"),
		Fraction (29.5735)
	)
	check_EQ (
		volume_swap.start ([ 1, "FL OZ" ], "liters"),
		Fraction (29.5735) * Fraction (1, 1000),
		is_float = True
	)
	check_EQ (
		volume_swap.start ([ 1, "liters" ], "fluid ounces"),
		Fraction (1, (Fraction (29.5735) * Fraction (1, 1000))),
		is_float = True
	)
	
	

def check_2 ():
	check_EQ (
		volume_swap.start ([ 1, "fluid OUNCES" ], "mL"),
		Fraction (29.5735)
	)
	check_EQ (
		volume_swap.start ([ 1, "FL OZ" ], "liters"),
		Fraction (29.5735) * Fraction (1, 1000),
		is_float = True
	)

	check_EQ (
		volume_swap.start ([ 1, "litres" ], "fluid ounces"),
		Fraction (1, (Fraction (29.5735) * Fraction (1, 1000))),
		is_float = True
	)

	return;
	
def check_3 ():
	'''
	EXCEPTION_CALLED = False
	try:
		check_EQ (
			volume_swap.start ([ 1, "fluid OUNCES" ], "ml"),
			Fraction (29.5735)
		)
		
	except Exception as E:
		assert (str (E) == "Unit 'ml' was not found.")
		EXCEPTION_CALLED = True

	assert (EXCEPTION_CALLED == True)
	'''

	
checks = {
	"fraction checks": check_1,
	"fraction checks, alternate spellings": check_2,
	"exceptions": check_3
}