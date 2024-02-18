

'''
import apoplast.clouds.food_USDA.deliveries.one as retrieve_1_food
retrieve_1_food.presently ()
'''

import json
import requests

import apoplast.clouds.food_USDA.deliveries.one.assertions.branded as assertions_branded
import apoplast.clouds.food_USDA.deliveries.one.assertions.foundational as assertions_foundational

import apoplast.clouds.food_USDA.deliveries.source as USDA_source


def presently (
	FDC_ID,
	API_ellipse = "",
	kind = "branded"
):
	host = 'https://api.nal.usda.gov'
	path = f'/fdc/v1/food/{ FDC_ID }'
	params = f'?api_key={ API_ellipse }'
	
	address = host + path + params
	
	print (
		"This ask is on track to be sent.", 
		json.dumps ({ "address": address }, indent = 2)
	)
	
	r = requests.get (address)
	print ("This response code was received.", r.status_code)
	
	data = json.loads (r.text)

	if (kind == "branded"):
		assertions_branded.run (data)
		
	elif (kind == "foundational"):
		assertions_foundational.run (data)

	return {
		"data": data,
		"source": USDA_source.find (FDC_ID)
	}
	


	#