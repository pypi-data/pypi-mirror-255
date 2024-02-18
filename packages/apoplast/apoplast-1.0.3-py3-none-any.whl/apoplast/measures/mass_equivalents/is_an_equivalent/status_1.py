





'''
	python3 insurance.py "measures/mass_equivalents/is_an_equivalent/status_1.py"
'''


import json
import apoplast.measures.mass_equivalents.is_an_equivalent as is_an_equivalent

def check_1 ():	
	assert (is_an_equivalent.calc ("mcg RAE") == True)
	assert (is_an_equivalent.calc ("mcg ne") == False)
	
checks = {
	"check 1": check_1
}