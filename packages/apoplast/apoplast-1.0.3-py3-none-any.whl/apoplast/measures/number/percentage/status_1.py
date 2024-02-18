
'''
	python3 insurance.py "measures/number/percentage/status_1.py"
'''


import apoplast.measures.number.percentage.from_fraction as percentage_from_fraction

from fractions import Fraction

def check_1 ():
	percent = percentage_from_fraction.calc (Fraction (1/3)) 
	assert (percent == "33.333%"), percent

	percent = percentage_from_fraction.calc (Fraction (1/2)) 
	assert (percent == "50.000%"), percent

	percent = percentage_from_fraction.calc (Fraction (1/7)) 
	assert (percent == "14.286%"), percent

	return;
	
	
checks = {
	"check 1": check_1
}