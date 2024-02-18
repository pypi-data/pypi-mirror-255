# -*- coding: utf-8 -*-
import yaml
from collections import defaultdict


class Atlas:
    def __new__( cls, item, *args, **kw  ):
        return _wrap( item )


class Chibi_atlas( dict ):
    """
    Clase para crear dicionarios para que sus keys sean leibles como
    atributos de classes
    """

    def __init__( self, *args, **kw ):
        for arg in args:
            if isinstance( arg, dict ):
                for k, v in arg.items():
                    self[ k ] = v
        for k, v in kw.items():
            self[ k ] = v

        # super().__init__( *args, **kw )

    def __getattr__( self, name ):
        try:
            return super().__getattribute__( name )
        except AttributeError as e:
            try:
                return self[ name ]
            except KeyError:
                raise e

    def __setattr__( self, name, value ):
        try:
            if getattr( type( self ), name, False ):
                super().__setattr__( name, value )
            else:
                self[ name ] = _wrap( value )
        except TypeError:
            self[ name ] = _wrap( value )

    def __delattr__( self, name ):
        del self[ name ]

    def __setitem__( self, name, value ):
        super().__setitem__( name, _wrap( value ) )

    def __dir__( self ):
        return list( self.keys() )


class Chibi_atlas_ignore_case( Chibi_atlas ):
    """
    clase que crea chibi atlas que son case insensitive
    """
    def __init__( self, *args, **kw ):
        args_clean = []
        for a in args:
            if isinstance( a, dict ) or hasattr( a, 'items' ):
                args_clean.append( { k.lower(): v for k, v in a.items() } )
        kw = { k.lower(): v for k, v in kw.items() }
        super().__init__( *args_clean, **kw )

    def __getattr__( self, name ):
        name = name.lower()
        return super().__getattr__( name )

    def __getitem__( self, key ):
        key = key.lower()
        return super().__getitem__( key )

    def __setattr__( self, name, value ):
        name = name.lower()
        return super().__setattr__( name, value )

    def __setitem__( self, key, value ):
        key = key.lower()
        return super().__setitem__( key, value )


def _default_factory():
    return Chibi_atlas_default()


class Chibi_atlas_default( defaultdict, Chibi_atlas ):
    """
    chibi atlas que emula `py:class:collections.defaultdict`
    """
    def __init__( self, default_factory=None, *args, **kw ):
        if default_factory is None:
            default_factory = _default_factory
        super().__init__( default_factory, *args, **kw )


class __Chibi_atlas_list( list ):
    def __getitem__( self, index ):
        value = super().__getitem__( index, )
        value = _wrap( value )
        self[ index ] = value
        return value

    def __iter__( self ):
        for i, v in enumerate( super().__iter__() ):
            value = _wrap( v )
            self[ i ] = value
            yield value


def _wrap( val, klass=None ):
    if type( val ) is dict:
        if klass is None:
            return Chibi_atlas( val )
        else:
            return klass( val )
    elif type( val ) is list:
        if klass is None:
            return __Chibi_atlas_list( val )
        else:
            return klass( val )
    return val


yaml.add_representer(
    Chibi_atlas, yaml.representer.SafeRepresenter.represent_dict )


yaml.add_representer(
    __Chibi_atlas_list, yaml.representer.SafeRepresenter.represent_list )
