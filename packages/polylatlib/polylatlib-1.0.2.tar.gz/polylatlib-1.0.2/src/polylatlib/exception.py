"""
**********
Exceptions
**********
Base exceptions and errors for PolyLat.
"""

__all__ = [
    "PolyLatError",
    "PolyLatNotCart",
    "PolyLatNotPosInt",
    "PolyLatNotColour",
    "PolyLatNotProp",
    "PolyLatNotExist",
]

class PolyLatError(Exception):
    """Base class for exceptions in PolyLat."""


class PolyLatNotCart(PolyLatError):
    """Raised when PolyLat expects a Cartesian coordinate and does not recieve one."""
    def __init__(self, coord):
        msg = f"'{coord}' is not a Cartesian Coordinate"
        super().__init__(msg)


class PolyLatNotPosInt(PolyLatError):
    """Raised when PolyLat expects a positive integer for drawing purposes."""
    def __init__(self, value):
        msg = f"'{value}' must be a positive integer."
        super().__init__(msg)


class PolyLatNotColour(PolyLatError):
    """Raised when PolyLat recieves a non-supported colour for drawing purposes."""
    def __init__(self, colour):
        msg = f"'{colour}' is not a supported colour."
        super().__init__(msg)
    

class PolyLatNotProp(PolyLatError):
    """Raised when PolyLat recieves an incorrect property."""
    def __init__(self, item):
        msg = f"'{item}' is not a property."
        super().__init__(msg)


class PolyLatNotExist(PolyLatError):
    """Raised when non-existent vector or edge is passed into PolyLat method."""
    def __init__(self, item):
        msg = f"'{item}' does not exist in the shape."
        super().__init__(msg)