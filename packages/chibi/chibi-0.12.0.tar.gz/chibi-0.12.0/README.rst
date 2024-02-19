=====
chibi
=====

this package is for i can put snippets and other useful things
and i do not need to write the same thing for fifth time

*************
cosas utitles
*************

Chibi_path
==========

the chibi path work like strings but with opperators have sense for folders
and files

.. code-block:: python

	from chibi.file import Chibi_path

	tmp = Chibi_path( '/tmp/folder' )
	isintance( p, str ) == true
	# return a generator with all the files and folders in
	# the path
	ls = list( p.ls() )
	print( ls )
	p = tmp + 'file.json'
	str( p ) == '/tmp/folder/file.json'
	f = p.open()
	# check the file for see is containt the string
	'some string' in f

	# write a dict like json in the file
	f.write( { 'stuff': 'str' } )
	# read the json and transform the dict in a Chibi_atlas
	json = f.read()
	json.stuff == 'str'

	# the same but in yaml
	f = p + 'file.yaml'
	f.write( { 'stuff': 'str' } )
	yaml = f.read()
	yaml.stuff == 'str'


Chibi_atlas
===========

esta herramienta se migro al paquete chibi-atlas

this is a dict but his keys can be access like attribute

.. code-block:: python

	import chibi.atals import Chibi_atlas


	c = Chibi_atlas( { 'stuff': 'str', 'l': [ 1, { 'more_stuff': 'str_2' } ] } )
	isintance( c, dict ) == true
	c.stuff == 'str'
	c.l[0] == 1
	c.l[1].more_stuff == 'str_2'
