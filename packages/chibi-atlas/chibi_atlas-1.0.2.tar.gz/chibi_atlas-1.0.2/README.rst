===========
chibi_atlas
===========

small lib to proccess the keys of the dict like attributes

.. image:: https://img.shields.io/pypi/v/chibi_atlas.svg
        :target: https://pypi.python.org/pypi/chibi_atlas

.. image:: https://img.shields.io/travis/dem4ply/chibi_atlas.svg
        :target: https://travis-ci.org/dem4ply/chibi_atlas

.. image:: https://readthedocs.org/projects/chibi-atlas/badge/?version=latest
        :target: https://chibi-atlas.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


this is a dict but his keys can be access like attribute

.. code-block:: python

	import chibi_atlas import Chibi_atlas


	c = Chibi_atlas( { 'stuff': 'str', 'l': [ 1, { 'more_stuff': 'str_2' } ] } )
	isintance( c, dict ) == true
	c.stuff == 'str'
	c.l[0] == 1
	c.l[1].more_stuff == 'str_2'

*****************
chibi_atlas_multi
*****************

Chibi_atlas_multi se utiliza para asumir que cada asignacion en cada key
seria asumiendo que su valor es una lista y se le hace append en el caso que
solo se le asigne un solo valor entonces usara el comportamiento por defecto
de los dicionarios

.. code-block:: python

	from chibi_atlas.multi import Chibi_atlas_multi

	c = Chibi_atlas_multi()
	c[ 'a' ] = 'a'
	assert { 'a': 'a' } == c

	c = Chibi_atlas_multi()
	c[ 'a' ] = 'a'
	c[ 'a' ] = 'b'
	c[ 'a' ] = 'c'
	assert { 'a': [ 'a', 'b', 'c', ] } == c


**********
Chibi_tree
**********

no recuerdo porque hice esta cosa pero funciona como un arbol con atributos


* Free software: WTFPL
* Documentation: https://chibi-atlas.readthedocs.io.
