




def add_paths_to_system (paths):
	import pathlib
	from os.path import dirname, join, normpath
	import sys
	
	this_directory = pathlib.Path (__file__).parent.resolve ()	
	for path in paths:
		sys.path.insert (0, normpath (join (this_directory, path)))

add_paths_to_system ([
	'../../../modules_pip'
])


import json
import pathlib
from os.path import dirname, join, normpath

module_name = "apoplast"

this_directory = pathlib.Path (__file__).parent.resolve ()
structures = str (normpath (join (this_directory, "../../../../structures")))
this_module = str (normpath (join (structures, f"modules/{ module_name }")))

#glob_string = structures + '/modules/**/status_*.py'

import sys
if (len (sys.argv) >= 2):
	glob_string = this_module + '/' + sys.argv [1]
	db_directory = False
else:
	glob_string = this_module + '/**/status_*.py'
	db_directory = normpath (join (this_directory, "db"))

print ("glob string:", glob_string)

import bracelet
scan = bracelet.start (
	glob_string = glob_string,
	simultaneous = True,
	module_paths = [
		normpath (join (structures, "modules")),
		normpath (join (structures, "modules_pip"))
	],
	relative_path = this_module,
	
	db_directory = db_directory
)
