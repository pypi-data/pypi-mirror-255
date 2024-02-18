


def run (data):
	assert ("description" in data)
	assert ("foodNutrients" in data)
	assert ("packageWeight" in data)
	
	
	
	#
	#	IF MORE THAN ONE
	#
	assert ("ingredients" in data)
	
	#
	#	RECOMMENDATIONS data
	#
	assert ("servingSize" in data)
	assert ("servingSizeUnit" in data)
	
	#
	#	SALES data
	#
	assert ("gtinUpc" in data)
	assert ("fdcId" in data)
	assert ("brandOwner" in data)
	assert ("brandName" in data)

	return;