



'''
	python3 insurance.py "measures/_interpret/status_unit_kind.py"
'''

import apoplast.measures._interpret.unit_kind as unit_kind

from fractions import Fraction

def check_1 ():
	assert (unit_kind.calc ("ml") == "volume")
	assert (unit_kind.calc ("fl oz") == "volume")
	
	assert (unit_kind.calc ("GRAM") == "mass")
	assert (unit_kind.calc ("gram") == "mass")
	
	assert (unit_kind.calc ("kcal") == "energy")
	assert (unit_kind.calc ("food calories") == "energy")
	assert (unit_kind.calc ("joules") == "energy")

	assert (unit_kind.calc ("IU") == "biological activity")
	assert (unit_kind.calc ("iu") == "biological activity")

checks = {
	"check 1": check_1
}
	


