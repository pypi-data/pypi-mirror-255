






'''
	import apoplast.clouds.supp_NIH.deliveries.one as NIH_API_one
	supplement = NIH_API_one.find (
		dsld_id,
		api_key
	)
	
	NIH_supplement_data = supplement ["data"]
	NIH_supplement_source = supplement ["source"]
'''


'''
	National Institutes of Health, Office of Dietary Supplements. 
	Dietary Supplement Label Database, 2023. https://dsld.od.nih.gov/. 
'''

import apoplast.clouds.supp_NIH.deliveries.source as NIH_API_source
import apoplast.clouds.supp_NIH.deliveries.one.assertions as assertions

import json

def find (
	DSLD_ID,
	api_key
):
	host = 'https://api.ods.od.nih.gov'
	path = f'/dsld/v9/label/{ DSLD_ID }'
	params = f'?api_key={ api_key }'
	
	coordinate = host + path + params

	print ("NIH supplement request is about to start.", json.dumps ({
		"coordinate": coordinate
	}, indent = 4))


	import requests
	response = requests.get (coordinate)

	print ("NIH returned response:", response.status_code)
	nih_supplement_data = json.loads (response.text)


	assertions.check (nih_supplement_data)

	return {
		"data": nih_supplement_data,
		"source": NIH_API_source.find (nih_supplement_data ["id"])
	}