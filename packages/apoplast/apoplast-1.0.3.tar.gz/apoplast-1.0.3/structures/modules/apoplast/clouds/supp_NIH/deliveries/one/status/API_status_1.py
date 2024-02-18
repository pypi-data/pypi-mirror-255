




'''
	python3 status_API.py "supp_NIH/deliveries/one/status/API_status_1.py"
'''


import json

import apoplast.clouds.supp_NIH.deliveries.one as NIH_API_one
import apoplast._ellipses as ellipses

def check_branded_1 ():
	API_NIH_ellipse = ellipses.scan () ['NIH'] ['supplements']
	supplement = NIH_API_one.find (220884, API_NIH_ellipse)
	
	
checks = {
	"NIH branded 1": check_branded_1
}