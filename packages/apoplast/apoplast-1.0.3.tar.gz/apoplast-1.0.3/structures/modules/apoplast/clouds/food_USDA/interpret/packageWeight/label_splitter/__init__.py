



def start (label):
	one = ""
	two = ""

	part_2 = False
	
	selector = 0
	last_index = len (label) - 1
	while (selector <= last_index):
		character = label [selector]
			
		if (character == " "):
			selector += 1
			break;
		else:	
			one += character
			
		selector += 1

	while (selector <= last_index):
		character = label [selector]
		two += character
		selector += 1
	
	return [ one.lower (), two.lower () ]