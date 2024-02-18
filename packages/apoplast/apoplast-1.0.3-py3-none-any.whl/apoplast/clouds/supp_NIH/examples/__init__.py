
'''
	import apoplast.clouds.supp_NIH.examples as NIH_examples
	NIH_example = NIH_examples.retrieve ("tablets/multivitamin_249664.JSON")
'''


def retrieve (path):
	import pathlib
	from os.path import dirname, join, normpath

	this_directory = pathlib.Path (__file__).parent.resolve ()
	example_path = normpath (join (this_directory, path))

	import json
	with open (example_path) as FP:
		data = json.load (FP)
	

	return data
	
	
'''
	# This is not tested.

	import apoplast.clouds.supp_NIH.examples as NIH_examples
	NIH_examples.add ("other/_.JSON", json.dumps ({}, indent = 4))
'''
def add (path, data):
	import pathlib
	from os.path import dirname, join, normpath

	this_directory = pathlib.Path (__file__).parent.resolve ()
	example_path = normpath (join (this_directory, path))

	FP = open (example_path, "w")
	FP.write (data)
	FP.close ()
	