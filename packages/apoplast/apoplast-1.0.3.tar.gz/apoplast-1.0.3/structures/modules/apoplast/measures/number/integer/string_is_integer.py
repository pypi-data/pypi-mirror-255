



'''
import apoplast.measures.number.integer.string_is_integer as string_is_integer
string_is_integer.check ("1234")
'''

def check (string):
	if (len (string) == 0):
		return False;
		
	integer_characters = [ 
		"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
	]
	for character in string:
		if (character not in integer_characters):
			return False;

	return True