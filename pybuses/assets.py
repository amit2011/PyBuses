
# Native libraries
from typing import Union, Optional, Callable, NewType

__all__ = [
    "Bus", "Stop",
    "StopGetter", "StopSetter", "StopDeleter",
    "BusGetter", "BusSetter", "BusDeleter",
]

# TODO This assets.py is the same as the one used on the API.
# API's assets.py might get imported from PyBuses?
# API's assets.py should be replaced with this one (is the same + better docstrings)


class Bus(object):
    """A Bus that will arrive to a Stop."""
    def __init__(
            self,
            line: str,
            route: str,
            time: Union[int, float],
            distance: Optional[Union[int, float]] = None
    ):
        """A Bus
        :param line: bus line (required)
        :param route: bus route (required)
        :param time: bus remaining time for reaching stop (required)
        :param distance: bus distance to stop (optional, default=None)
        :type line: str
        :type route: str
        :type time: int
        :type distance: int or None
        .. note:: All data types will be casted
        """
        self.line: str = str(line).strip()
        self.route: str = str(route).strip()
        self.time: int = int(time)
        self.distance: int = None
        if distance is not None:
            self.distance: int = int(distance)


class Stop(object):
    """A bus Stop, identified by a Stop ID. Buses will arrive to it."""
    def __init__(
            self,
            stopid: Union[int, str],
            name: str,
            lat: Union[float, str, None] = None,
            lon: Union[float, str, None] = None
    ):
        """
        :param stopid: Stop ID/Number (required)
        :param name: Stop name (not required for reference to custom stop getters)
        :param lat: Stop location latitude (optional, default=None)
        :param lon: Stop location longitude (optional, default=None)
        :type stopid: int
        :type name: str or None
        :type lat: float or None
        :type lon: float or None
        .. note:: All data types will be casted
        """
        self.stopid: int = int(stopid)
        self.id: int = self.stopid
        self.name: str = str(name).strip() if name else None  # QUESTION Reference to custom stop getters?
        if (lat, lon) == (None, None):
            self.lat = None
            self.lon = None
        else:
            self.lat: float = float(lat)
            self.lon: float = float(lon)

    def has_location(self) -> bool:
        """Check if this Stop has a valid location set (latitude and longitude)
        :return: True if Stop has both Latitude & Longitude values, False if one or both are missing
        :rtype: bool
        """
        return not (self.lat, self.lon) == (None, None)


# https://docs.python.org/3/library/typing.html#newtype
# StopGetterClassVar = ClassVar[Callable[[int], Stop]]
StopGetter = NewType("StopGetter", Callable[[int], Stop])
StopSetter = NewType("StopSetter", Callable[[Stop], None])
StopDeleter = NewType("StopDeleter", Callable[[int], bool])
BusGetter = NewType("BusGetter", Callable)
BusSetter = NewType("BusSetter", Callable)
BusDeleter = NewType("BusDeleter", Callable)
