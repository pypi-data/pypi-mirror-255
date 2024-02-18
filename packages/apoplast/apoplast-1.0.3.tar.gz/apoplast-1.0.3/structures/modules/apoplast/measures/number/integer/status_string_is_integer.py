




'''
	python3 insurance.py "measures/number/integer/status_string_is_integer.py"
'''

import apoplast.measures.number.integer.string_is_integer as string_is_integer

def check_1 ():
	assert (string_is_integer.check ("1234") == True)
	assert (string_is_integer.check ("0") == True)
	assert (string_is_integer.check ("1234781902394871293750182374") == True)
	
	assert (string_is_integer.check ("") == False)
	assert (string_is_integer.check ("1234.43") == False)
	assert (string_is_integer.check ("Z") == False)

	return;
	
	
checks = {
	"check 1": check_1
}