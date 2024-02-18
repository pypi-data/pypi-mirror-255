import pprint
from typing import Optional

from h2o_engine_manager.clients.convert import quantity_convertor
from h2o_engine_manager.gen.model.v1_constraint_numeric import V1ConstraintNumeric


class NumericConstraint:
    def __init__(self, minimum: str, default: str, maximum: Optional[str] = None):
        self.minimum = minimum
        self.default = default
        self.maximum = maximum

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def to_api_object(self):
        maximum = None
        if self.maximum is not None:
            maximum = quantity_convertor.quantity_to_number_str(self.maximum)
        return V1ConstraintNumeric(
            min=quantity_convertor.quantity_to_number_str(self.minimum),
            default=quantity_convertor.quantity_to_number_str(self.default),
            max=maximum,
        )


def from_api_object(api_object: V1ConstraintNumeric) -> NumericConstraint:
    maximum = None
    if api_object.max is not None:
        maximum = quantity_convertor.number_str_to_quantity(api_object.max)
    return NumericConstraint(
        minimum=quantity_convertor.number_str_to_quantity(api_object.min),
        default=quantity_convertor.number_str_to_quantity(api_object.default),
        maximum=maximum,
    )
