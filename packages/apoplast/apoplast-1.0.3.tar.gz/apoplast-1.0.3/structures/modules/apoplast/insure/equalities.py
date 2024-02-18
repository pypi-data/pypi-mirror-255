
'''
	priority:
	
		import apoplast.insure.equalities as equalities
		if (equalities.check ([
			[ 1, 1 ]
		])):	
'''


'''
		equalities.check ([
			[ 1, 1 ]
		], effect = "exception")
'''

def check (	
	* positionals,
	
	effect = "", 
	records = 1
):
	if (type (positionals [0]) == list):
		label = "unnamed equality check"
		checks = positionals [0]
		
	elif (type (positionals [1]) == list and type (positionals [1] == str)):
		label = positionals [0]
		checks = positionals [1]
	
	else:	
		raise Exception ("The arguments sent to insure/equalities could not be interpretted.")
	
	index = 0
	for check in checks:
		if (check [0] != check [1]):		
			if (effect == "exception"):
				print ("check [0]:", check [0])
				print ("check [1]:", check [1])
				raise Exception (f'"{ label }" An inequality was found at index: "{ index }"')
			
			else:
				if (records >= 1):
					print ()
					print (f'"{ label }" An inequality was found at index:', index)
					print ("	check [0]:", check [0])
					print ("	check [1]:", check [1])
			
				return False
				
		index += 1
			
	return True