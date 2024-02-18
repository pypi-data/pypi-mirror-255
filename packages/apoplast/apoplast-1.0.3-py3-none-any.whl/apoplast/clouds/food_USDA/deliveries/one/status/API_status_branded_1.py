

'''
python3 status_api.py "food/USDA/API/one/status/API_STATUS_branded_1.py"
'''

import json

import apoplast.clouds.food_USDA.deliveries.one as retrieve_1_food
import apoplast._ellipses as ellipses

def check_branded_1 ():	
	API_USDA_ellipse = ellipses.scan () ['USDA'] ['food']
	
	food = retrieve_1_food.presently (
		2642759,
		API_ellipse = API_USDA_ellipse
	)

	
checks = {
	"check branded 1": check_branded_1
}