import datetime
from numbers import Number
from halo_app.classes import AbsBaseClass

from dataclasses import dataclass

#{"field": "<field_name>", "op": "<operator>", "value": "<some_value>"}
from halo_app.exceptions import FilterValidationException

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

class AbsFilter(AbsBaseClass):
    pass


@dataclass
class Filter(AbsFilter):
    field: str
    op: str
    value: object

    def is_valid(self,value):
        try:
            allowed = (Number, datetime.date, datetime.datetime)
            return isinstance(value, allowed)
        except AssertionError:
            raise FilterValidationException(f"{self} requires an ordinal value")

    def is_valid_list(self,value):
        try:
            allowed = ([])
            return isinstance(value, allowed)
        except AssertionError:
            raise FilterValidationException(f"{self} requires an ordinal value")

    def apply(self, value):
        if self.op == '<' and self.is_valid(value):
            return value < self.value

        if self.op == '>' and self.is_valid(value):
            return value > self.value

        if self.op == '<=' and self.is_valid(value):
            return value <= self.value

        if self.op == '>=' and self.is_valid(value):
            return value >= self.value

        if self.op == '=':
            return value == self.value

        if self.op == '!=':
            return value != self.value

        if self.op == 'in' and self.is_valid_list(value):
            return value in self.value

        #if self.op == 'like' and self.is_valid_list(value):
        #    return value like self.value

        #if self.op == 'contains' and self.is_valid_list(value):
        #    return value contains self.value





