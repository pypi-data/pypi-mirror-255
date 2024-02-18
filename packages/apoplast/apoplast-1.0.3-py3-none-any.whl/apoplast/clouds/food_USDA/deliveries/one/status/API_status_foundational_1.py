

'''
python3 status_api.py "food/USDA/API/one/status/API_STATUS_foundational_1.py"
'''


import json

import apoplast.clouds.food_USDA.deliveries.one as retrieve_1_food
import apoplast._ellipses as ellipses


def check_foundational_1 ():
	API_USDA_ellipse = ellipses.scan () ['USDA'] ['food']
	
	food = retrieve_1_food.presently (
		2515381,
		API_ellipse = API_USDA_ellipse,
		kind = "foundational"
	)

	
checks = {
	"check foundational 1": check_foundational_1
}