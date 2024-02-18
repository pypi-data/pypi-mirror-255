
'''
	python3 insurance.py "measures/mass/swap/status_1.py"
'''

import apoplast.measures.mass.swap as mass_swap

from fractions import Fraction

def CHECK_1 ():
	assert (float (mass_swap.start ([ 453.59237, "GRAMS" ], "POUNDS")) == 1.0)
	assert (float (mass_swap.start ([ 453.59237, "grams" ], "pounds")) == 1.0)	
	assert (float (mass_swap.start ([ 453.59237, "Gram(s)" ], "pounds")) == 1.0)	
	
	assert (float (mass_swap.start ([ 10, "OUNCES" ], "POUNDS")) == 0.625)
	assert (float (mass_swap.start ([ 10, "OUNCES" ], "GRAMS")) == 283.49523125)	


	assert (
		float (mass_swap.start ([ 1, "pounds" ], "grams")) == 453.59237
	), float (mass_swap.start ([ 1, "pounds" ], "grams")) 
	


	
def CHECK_2 ():
	assert (
		mass_swap.start ([ 10, "mcg" ], "g") == 
		Fraction (1, 100000)
	)	
	assert (
		mass_swap.start ([ 10, "mcg" ], "mg") == 
		Fraction (1, 100)
	)	
	
	assert (
		mass_swap.start ([ 10, "mg" ], "g") == 
		Fraction (1, 100)
	)
	
	assert (
		mass_swap.start ([ 10, "g" ], "mg") == 
		Fraction (10000, 1)
	)
	assert (
		mass_swap.start ([ 10, "g" ], "mcg") == 
		Fraction (10000000, 1)
	)
	
checks = {
	"CHECK 1": CHECK_1,
	"CHECK 2": CHECK_2
}