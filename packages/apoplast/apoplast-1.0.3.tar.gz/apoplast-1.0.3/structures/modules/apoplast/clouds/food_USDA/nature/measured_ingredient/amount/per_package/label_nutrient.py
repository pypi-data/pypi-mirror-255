
'''
	label_nutrient_calculator.calc (
		USDA_label_nutrient = "fiber": {
			"value": 1.99
		},
		servings_per_package = 4
	)
'''
def calc (
	USDA_label_nutrient,
	servings_per_package
):
	assert ("value" in USDA_label_nutrient)
	USDA_label_nutrient_amount = USDA_label_nutrient ["value"]
	
	mass_plus_mass_eq_per_package__from_label = (
		Fraction (USDA_label_nutrient_amount) *
		Fraction (servings_per_package)
	)

	return mass_plus_mass_eq_per_package__from_label;