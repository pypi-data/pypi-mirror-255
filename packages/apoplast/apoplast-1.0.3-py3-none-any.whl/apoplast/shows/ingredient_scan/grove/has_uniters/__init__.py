
'''
	import apoplast.shows.ingredient_scan.grove.has_uniters as has_uniters
	has_uniters.check (grove)
'''

'''
	description:
		This is meant for checking on 1 food or 1 supplement,
		to assess whether additions need to be made to uniters.
'''

'''
	priorities:
		This make sure there are no missing intermediaries in the grove.
'''
import apoplast.shows.ingredient_scan.grove.seek as grove_seek
import apoplast.shows.ingredient_scan.grove.seek_uniter as seek_uniter

import apoplast.shows.ingredient_scan.grove.essential_is_story_1 as essential_is_story_1
	
import json	
	
def check (grove, return_problem = False):
	story_1_list = essential_is_story_1.generate_list (grove)

	checked = []

	def for_each (entry):	
		nonlocal return_problem;
	
		name = entry ["info"] ["names"] [0]
		if (essential_is_story_1.check (story_1_list, name) == False):
			uniter = seek_uniter.beautifully (
				grove = grove,
				name = name
			)		
			assert (type (uniter) == dict)	

			checked.append ([
				name, 
				uniter ["info"] ["names"][0]
			])

			'''
			print ("checking:", 
				name, 
				uniter ["info"] ["names"][0],
				entry ["natures"], 
				uniter ["natures"]
			)
			'''
			
			if (len (entry ["natures"]) >= 1):
				if (len (uniter ["natures"]) == 0 ):
					print (f"""
					
	The uniter '{ uniter ["info"] ["names"] }' is comprised of 
	'{ len (uniter ["natures"]) }' natures.
	
	It unites '{ entry ["info"] ["names"] }' which has 
	'{ len (entry ["natures"]) }' natures.				
					
					""")
					
					'''
						possibly where: {
							"amount": "1",
							"source": {
								"name": "",
								"FDC ID": "",
								"UPC": "",
								"DSLD ID": ""
							},
							"ingredient": {
								"name": "added sugars"
							},
							"measures": {
								"mass + mass equivalents": {
									"per package": {
										"listed": [
											"1947.660",
											"mg"
										],
										"grams": {
											"decimal string": "1.948",
											"fraction string": "97383/50000"
										}
									}
								}
							}
						}
						
						Add the "measures" of "added sugar"
						towards the first story of the grove,
						until a uniter with natures is found.
						
							Therefore, if dietary fiber and carbohydrates
							both do not have natures, then add 
							the "measures" ("mass + mass equivalents")
							of "added "sugars" to "dietary fiber"
							and then to "carbohydrates"
						
								for example:
									This:
										carbs = 0g
											dietary fiber = 0g
												added sugars = 10g
									
									Becomes:
										carbs = 10g
											dietary fiber = 10g
												added sugars = 10g		
								
						
							Alternatively, if carbohydrates has 
							natures and dietary fiber doesn't,
							then perhaps assume that the 
							"measures" of "added sugars" are
							already included in carbohydrates.
							
								for example:
									This:
										carbs = 20g
											dietary fiber = 0g
												added sugars = 10g
									
									Becomes:
										carbs = 20g
											dietary fiber = 10g
												added sugars = 10g	
						
						
						add this: {
							"amount": "1",
							"source": {
								"name": "",
								"FDC ID": "",
								"UPC": "",
								"DSLD ID": ""
							},
							"ingredient": {
								"name": "dietary fiber",
								"added from measures of united": "added sugars"
							},
							"measures": {
								"mass + mass equivalents": {
									"per package": {
										"listed": [
											"1947.660",
											"mg"
										],
										"grams": {
											"decimal string": "1.948",
											"fraction string": "97383/50000"
										}
									}
								}
							}
						}
						
						add this: {
							"amount": "1",
							"source": {
								"name": "",
								"FDC ID": "",
								"UPC": "",
								"DSLD ID": ""
							},
							"ingredient": {
								"name": "carbohydrates",
								"added from measures of united": "added sugars"
							},
							"measures": {
								"mass + mass equivalents": {
									"per package": {
										"listed": [
											"1947.660",
											"mg"
										],
										"grams": {
											"decimal string": "1.948",
											"fraction string": "97383/50000"
										}
									}
								}
							}
						}
					'''
					
					if (return_problem):
						return True
					
					print ('natures:', json.dumps (entry ["natures"], indent = 4))
					
					entry_name = entry ["info"] ["names"]
					raise Exception (f"Uniter nature not found for '{ entry_name }'")
					
					
			
	
	problem = grove_seek.beautifully (
		grove = grove,
		for_each = for_each
	)
	
	return {
		"checked": checked,
		"problem": problem
	}
