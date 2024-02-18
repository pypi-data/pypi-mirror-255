


def check (nih_supplement_data):
	assert ("ingredientRows" in nih_supplement_data)
	assert ("servingSizes" in nih_supplement_data)
	assert ("statements" in nih_supplement_data)
	assert ("netContents" in nih_supplement_data)
	assert ("servingsPerContainer" in nih_supplement_data)
	
	assert ("otheringredients" in nih_supplement_data)
	assert ("ingredients" in nih_supplement_data ["otheringredients"])

	assert ("statements" in nih_supplement_data)
	assert ("upcSku" in nih_supplement_data)
	assert ("id" in nih_supplement_data)	
	
	assert ("brandName" in nih_supplement_data)
	assert ("fullName" in nih_supplement_data)
	assert ("contacts" in nih_supplement_data)

	assert ("userGroups" in nih_supplement_data)
	
	assert ("servingSizes" in nih_supplement_data)
	assert (len (nih_supplement_data ["servingSizes"]) == 1)
	assert ("minQuantity" in nih_supplement_data ["servingSizes"][0])
	assert ("maxQuantity" in nih_supplement_data ["servingSizes"][0])
	assert ("unit" in nih_supplement_data ["servingSizes"][0])
	assert ("notes" in nih_supplement_data ["servingSizes"][0])

	return;