

'''
	status_multivitamin_276336
'''
'''
	python3 insurance.py clouds/supp_NIH/nature/_status/_loop/status_1.py
'''

import apoplast.clouds.supp_NIH.nature as supp_NIH_nature
import apoplast.clouds.supp_NIH.examples as NIH_examples

import json

def check_1 ():	
	loop = [
		"coated tablets/multivitamin_276336.JSON",
		"other/chia_seeds_214893.JSON",
		"powder/mane_270619.JSON",
		"powder/nutritional_shake_220884.JSON",
		"powder packets/multivitamin_246811.JSON",
		#"tablets/calcium_261967.JSON",
		#"tablets/multivitamin_249664.JSON",
		#"vegan_capsules/probiotics_248267.JSON"
	]
	
	for supp in loop:
		supp_1 = supp_NIH_nature.create (
			NIH_examples.retrieve (supp)
		)
		

	
	return;
	
checks = {
	"check 1": check_1
}