
'''
	from apoplast.insure.override_print import override_print
'''

from __future__ import print_function
def override_print ():
	import builtins	
	import inspect
	import os
	import pathlib
	from os.path import dirname, join, normpath
	import sys
	

	this_folder = pathlib.Path (__file__).parent.resolve ()	

	builtin_print = builtins.print
	def print (*args, **kwargs):
		this_folder = pathlib.Path (__file__).parent.resolve ()	
		abs_path = os.path.abspath ((inspect.stack () [1])[1])
		
		relative_caller_path = os.path.relpath (
			os.path.abspath ((inspect.stack () [1])[1]),
			this_folder
		)
		
		builtin_print ()
		builtin_print (abs_path)
		builtin_print ("	override", *args, **kwargs)

	   
	builtins.print = print	

