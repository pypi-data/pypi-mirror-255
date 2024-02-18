

'''
	import apoplast._ellipses as ellipses
	API_USDA_ellipse = ellipses.scan () ['USDA'] ['food']
	API_NIH_ellipse = ellipses.scan () ['NIH'] ['supplements']
'''

'''
{
	"USDA": {
		"food": ""
	},
	"NIH": {
		"supplements": ""
	}
}
'''

ellipsis_path = "/offline/crowns_safes/mint/apoplast/ellipsis.json"

import json
fp = open (ellipsis_path, "r")
bounce = json.loads (fp.read ())
fp.close ()


def scan ():
	return bounce