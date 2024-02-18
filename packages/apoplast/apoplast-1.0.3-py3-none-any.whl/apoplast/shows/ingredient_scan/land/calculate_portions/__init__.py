
'''
	description:
		This maybe can be used for calculating the portions of one treasure
		or multiple treasures.
	
		previously:
			This should be for calculating the land measures sum of 1 treasure,
			where that 1 treasure only has 1 package.
'''

'''
	import apoplast.shows.ingredient_scan.land.calculate_portions as calculate_portions
	calculate_portions.illustriously (
		land = land
	)
'''

'''
{
	"amount": "1",
	"source": {
		"name": "WALNUTS HALVES & PIECES, WALNUTS",
		"FDC ID": "1882785",
		"UPC": "099482434618",
		"DSLD ID": ""
	},
	"ingredient": {
		"name": "Iron, Fe"
	},
	"measures": {
		"mass + mass equivalents": {
			"per package": {
				"listed": [
					"12.984",
					"mg"
				],
				"grams": {
					"decimal string": "0.013",
					"fraction string": "1461913475040736643/112589990684262400000",
				}
			},
			"portion of grove": {
				"fraction string": "1/2"
				"decimal string": ""
			}
		}
	}
}
'''
	
from fractions import Fraction
	
def illustriously (
	land = {}
):
	grove = land ['grove']
	land_measures = land ['measures']
	
	for ingredient in grove:
		ingredient_name_0 = ingredient ["info"]["names"][0]
		
		'''
		if (len (ingredient ["natures"]) == 0):
			continue;
		if (len (ingredient ["natures"]) >= 2):
			raise Exception (f"This def is for calculating the sum of a grove with only 1 treasure (food or supp) added")
		
		number_of_packages = Fraction (
			ingredient ["natures"] [ 0 ] ["amount"]
		)
		assert (number_of_packages == 1)
		'''
		
		ingredient_measures = ingredient ["measures"]
		for measure_name in ingredient_measures:
			ingredient_measure = ingredient_measures [ measure_name ]
	
			if (measure_name in [ "biological activity" ]):
				continue;
			if (measure_name in [ "mass + mass equivalents", "energy" ]):
				if (measure_name == "mass + mass equivalents"):
					unit = "grams"
				elif (measure_name == "biological activity"):
					unit = "IU"
				elif (measure_name == "energy"):
					unit = "food calories"
				else:
					raise Exception ("?")
			else:
				raise Exception (f"Measure: '{ measure_name }' was not accounted for.") 
			
			
			
			assert (
				Fraction (land_measures [ measure_name ] [ "per recipe" ] [ unit ] [ "fraction string" ]) >= 0
			), land_measures [ measure_name ] [ "per recipe" ] [ unit ] [ "fraction string" ]
			
			numerator = (
				Fraction (ingredient_measure ["per recipe"] [ unit ] [ "fraction string" ])
			)
			
			'''
				This could be zero if for example:
				
					ingredient amount = 0
					
					therefore, sum = 0
					
					ergo:
						ingredient / sum = 0 / 0
			'''
			denomenator = Fraction (
				land_measures [ measure_name ] [ "per recipe" ] [ unit ] [ "fraction string" ]
			)
			
			if (denomenator == 0):
				portion = 0;
			else:
				portion = Fraction (
					numerator,
					denomenator
				)
			
			ingredient_measure ["portion of grove"] = {
				"fraction string": str (portion),
				#"decimal string": ""
			}
			
			print (f'[portion calc] "{ float (portion) }" measure "{ measure_name }" of "{ ingredient_name_0 }"')
			
			
			#print ("	porition:", float (portion))
			
	return;