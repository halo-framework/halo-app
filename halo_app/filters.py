from halo_app.classes import AbsBaseClass

from dataclasses import dataclass

#{"field": "<field_name>", "op": "<operator>", "value": "<some_value>"}

"""
symbol  operator	
<	    less-than	
<=	    less-than or equal to	
=	    equal to	
>	    greater-than	
>=	    greater-than or equal to	
in	    in	
!=	    not equal to	
like	like	
contains	many-to-many associated	
"""
@dataclass
class Filter(AbsBaseClass):
    field: str
    op: str
    value: object



