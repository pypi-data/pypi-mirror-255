from . import Chibi_atlas


class Chibi_atlas_multi( Chibi_atlas ):
    def __setitem__( self, name, value ):
        if name in self:
            current = self[ name ]
            if not isinstance( current, list ):
                current = [ current ]
                del self[ name ]
                self[ name ] = current
            self[ name ].append( value )
        else:
            super().__setitem__( name, value )

    def update( self, d ):
        if not isinstance( d, dict ):
            raise NotImplementedError(
                f"no esta implementado el typo {type(d)}" )
        for k, v in d.items():
            self[ k ] = v
