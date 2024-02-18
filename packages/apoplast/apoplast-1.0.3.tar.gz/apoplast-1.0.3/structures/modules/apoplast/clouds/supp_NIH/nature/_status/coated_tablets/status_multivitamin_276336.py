

'''
	status_multivitamin_276336
'''
'''
	python3 insurance.py clouds/supp_NIH/nature/_status/coated_tablets/status_multivitamin_276336.py
'''



import json

def check_1 ():	
	import apoplast.clouds.supp_NIH.nature as supp_NIH_nature
	import apoplast.clouds.supp_NIH.examples as NIH_examples
	supp_1 = supp_NIH_nature.create (
		NIH_examples.retrieve ("coated tablets/multivitamin_276336.JSON")
	)
	
	print (json.dumps (supp_1, indent = 4))
	
	def add (path, data):
		import pathlib
		from os.path import dirname, join, normpath
		this_directory = pathlib.Path (__file__).parent.resolve ()
		example_path = normpath (join (this_directory, path))
		FP = open (example_path, "w")
		FP.write (data)
		FP.close ()
		
	add ("status_multivitamin_276336_nature.JSON", json.dumps (supp_1, indent = 4))
	
	return;
	
checks = {
	"check 1": check_1
}