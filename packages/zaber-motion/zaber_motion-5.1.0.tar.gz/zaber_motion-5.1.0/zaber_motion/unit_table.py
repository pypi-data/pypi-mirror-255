# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .call import call_sync
from .protobufs import main_pb2
from .units import Units, UnitsAndLiterals, units_from_literals


class UnitTable:
    """
    Helper for working with units of measure.
    """

    @staticmethod
    def get_symbol(
            unit: UnitsAndLiterals
    ) -> str:
        """
        Gets the standard symbol associated with a given unit.

        Args:
            unit: Unit of measure.

        Returns:
            Symbols corresponding to the given unit. Throws NoValueForKey if no symbol is defined.
        """
        request = main_pb2.UnitGetSymbolRequest()
        request.unit = units_from_literals(unit).value
        response = main_pb2.UnitGetSymbolResponse()
        call_sync("units/get_symbol", request, response)
        return response.symbol

    @staticmethod
    def get_unit(
            symbol: str
    ) -> UnitsAndLiterals:
        """
        Gets the unit enum value associated with a standard symbol.
        Note not all units can be retrieved this way.

        Args:
            symbol: Symbol to look up.

        Returns:
            The unit enum value with the given symbols. Throws NoValueForKey if the symbol is not supported for lookup.
        """
        request = main_pb2.UnitGetEnumRequest()
        request.symbol = symbol
        response = main_pb2.UnitGetEnumResponse()
        call_sync("units/get_enum", request, response)
        return Units(response.unit)
