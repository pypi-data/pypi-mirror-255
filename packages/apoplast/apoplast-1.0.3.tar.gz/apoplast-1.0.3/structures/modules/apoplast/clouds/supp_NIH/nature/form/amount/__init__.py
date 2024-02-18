



'''
	import apoplast.clouds.supp_NIH.nature.form.amount as form_amount
	form_amount.calc (
		net_contents
		form_unit
	)
'''


def find_grams_quantity (net_contents):
	for net_content in net_contents:
		if (net_content ["unit"] == "Gram(s)"):
			return str (net_content ["quantity"])

	raise Exception (
		f"Quantity of grams could not be found in net_contents { net_contents }"
	)
	

def calc (
	net_contents,
	form_unit
):	
	if (form_unit == "gram"):
		return find_grams_quantity (
			net_contents
		)
	
	if (
		len (net_contents) == 1
	):
		return str (net_contents [0] ["quantity"])
		
	raise Exception ("The form quantity of the supplement could not be calculated.")
