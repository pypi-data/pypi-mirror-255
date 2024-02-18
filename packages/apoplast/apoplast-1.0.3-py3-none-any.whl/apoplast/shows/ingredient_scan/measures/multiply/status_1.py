





'''
	python3 insurance.py shows/ingredient_scan/measures/multiply/status_1.py
'''

import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import apoplast.clouds.food_USDA.examples as USDA_examples	
import apoplast.clouds.food_USDA.nature as food_USDA_nature
import apoplast.insure.equality as equality

import apoplast.shows.ingredient_scan.measures.multiply as multiply_measures

import json	

def check_1 ():
	measures = {
		"mass + mass equivalents": {
			"per package": {
				"grams": {
					"fraction string": "100/10"
				}
			}
		}
	}
	multiply_measures.effortlessly (
		amount = 9,
		measures = measures
	)
	assert (
		measures ["mass + mass equivalents"] ["per package"] ["grams"] ["fraction string"] ==
		"90"
	)
	
def check_2 ():
	measures = {
		"mass + mass equivalents": {
			"per recipe": {
				"grams": {
					"fraction string": "99400"
				}
			}
		},
		"biological activity": {
			"per recipe": {
				"IU": {
					"fraction string": "1300900"
				}
			}
		},
		"energy": {
			"per recipe": {
				"calories": {
					"fraction string": "1000000"
				},
				"joules": {
					"fraction string": "4184000"
				}
			}
		}
	}
	multiply_measures.effortlessly (
		amount = 10,
		measures = measures
	)
	assert (
		measures ["mass + mass equivalents"] ["per recipe"] ["grams"] ["fraction string"] ==
		"994000"
	)
	assert (
		measures ["biological activity"] ["per recipe"] ["IU"] ["fraction string"] ==
		"13009000"
	)
	assert (
		measures ["energy"] ["per recipe"] ["calories"] ["fraction string"] ==
		"10000000"
	)
	assert (
		measures ["energy"] ["per recipe"] ["joules"] ["fraction string"] ==
		"41840000"
	)
	
checks = {
	'check 1': check_1,
	'check 2': check_2
}