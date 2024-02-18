




def add_paths_to_system (paths):
	import pathlib
	from os.path import dirname, join, normpath
	import sys
	
	this_directory_path = pathlib.Path (__file__).parent.resolve ()	
	for path in paths:
		sys.path.insert (0, normpath (join (this_directory_path, path)))

add_paths_to_system ([
	'../../../modules',
	'../../../modules_pip'
])


import json
import pathlib
from os.path import dirname, join, normpath


name = "this_module"

this_directory_path = pathlib.Path (__file__).parent.resolve ()
structures_path = str (normpath (join (this_directory_path, "../../../../structures_path")))

this_module = str (normpath (join (structures_path, "modules", name)))

#status_assurances_path = str (normpath (join (this_directory_path, "insurance")))
status_assurances_path = str (normpath (join (this_directory_path, "..")))

import sys
if (len (sys.argv) >= 2):
	glob_string = status_assurances_path + '/' + sys.argv [1]
	db_directory = False
else:
	glob_string = status_assurances_path + '/**/status_*.py'
	db_directory = normpath (join (this_directory_path, "DB"))

print ("glob string:", glob_string)

import bracelet
scan = bracelet.start (
	glob_string = glob_string,
	simultaneous = True,
	module_paths = [
		normpath (join (structures_path, "modules")),
		normpath (join (structures_path, "modules_pip"))
	],
	relative_path = status_assurances_path,
	
	db_directory = db_directory
)
