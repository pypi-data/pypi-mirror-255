
'''
	import apoplast.shows.ingredient_scan.measures.multiply as multiply_measures
	multiply_measures.effortlessly (
		amount = 10,
		measures = measures
	)
'''

'''
	"mass + mass equivalents" 
		"grams"
'''

from fractions import Fraction

def effortlessly (measures, amount):
	for measure in measures:
		pers = measures [ measure ]
		
		for per in pers:
			units = pers [per]
		
			if (per == "portion of grove"):
				continue;
		
			if (per not in [ "per package", "per recipe" ]):
				raise Exception (f"The divisor found, '{ per }', was not accounted for.");
			
			for unit in units:
				measures [ measure ] [per] [unit] ["fraction string"] = str (
					Fraction (measures [ measure ] [per] [unit] ["fraction string"]) * Fraction (amount)
				)
				
	return measures;

