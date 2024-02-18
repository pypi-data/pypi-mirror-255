

'''
	https://fdc.nal.usda.gov/api-guide.html#bkmk-5
'''
def find (FDC_ID):
	return {
		"name": "USA USDA",
		"link": f"https://fdc.nal.usda.gov/fdc-app.html#/food-details/{ FDC_ID }/nutrients",
		"api": "https://fdc.nal.usda.gov/api-guide.html",
		"text": "U.S. Department of Agriculture, Agricultural Research Service. FoodData Central, 2019. fdc.nal.usda.gov."
	}
	
