
'''
	def relative_path (path):
		import pathlib
		from os.path import dirname, join, normpath
		import sys

		this_directory_path = pathlib.Path (__file__).parent.resolve ()	
		return str (normpath (join (this_directory_path, path)))
'''

'''
	import ramps_majestic.furniture.places as places
	places.relative_path ()
'''

def relative_path (path):
	import pathlib
	from os.path import dirname, join, normpath
	import sys

	this_directory_path = pathlib.Path (__file__).parent.resolve ()	
	return str (normpath (join (this_directory_path, path)))

