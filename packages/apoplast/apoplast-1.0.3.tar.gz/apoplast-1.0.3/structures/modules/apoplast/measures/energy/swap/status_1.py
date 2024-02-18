

'''
	python3 insurance.py "measures/energy/swap/status_1.py"
'''

import apoplast.measures.energy.swap as energy_swap

from fractions import Fraction 


def check_1 ():
	assert (
		energy_swap.start ([ 1, "food calorie" ], "joules") ==
		4184
	)
	
	assert (
		energy_swap.start ([ 1, "joules" ], "food calories") ==
		Fraction (1, 4184)
	)

	return;
	
checks = {
	'check 1': check_1
}