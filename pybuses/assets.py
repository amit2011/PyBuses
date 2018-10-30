
# Native libraries
from typing import Union, Optional, Callable, List, NewType, Dict

__all__ = [
    "Bus", "Stop",
    "StopGetter", "StopSetter", "StopDeleter",
    "BusGetter", "BusSetter", "BusDeleter",
]

# TODO This assets.py is the same as the one used on the API.
# API's assets.py might get imported from PyBuses?
# API's assets.py should be replaced with this one (is the same + better docstrings)


class Bus(object):
    """A Bus that will arrive to a Stop, or that is available on the bus service as a line-route."""
    def __init__(
            self,
            line: str,
            route: str,
            time: Optional[Union[int, float]] = None,
            distance: Optional[Union[int, float]] = None,
            other: Optional[Dict] = None
    ):
        """A Bus
        :param line: bus line (required)
        :param route: bus route (required)
        :param time: bus remaining time for reaching stop (optional, default=None)
        :param distance: bus distance to stop (optional, default=None)
        :param other: additional data for the Bus object, as a dict (optional, default=empty dict)
        :type line: str
        :type route: str
        :type time: int or float or None
        :type distance: int or float or None
        :type other: dict
        .. note:: Line and Route values will be casted and strip on __init__
        """
        self.line: str = str(line).strip()
        self.route: str = str(route).strip()
        self.time: Optional[Union[int, float]] = time
        self.distance: Optional[Union[int, float]] = distance
        self.other: Dict = other if other is not None else dict()

    def asdict(self) -> Dict:
        """Return all the data available about this Bus as a dict.
        Parameters where values are None will be hidden.
        :return: all parameters of this Bus object as a dict
        :rtype: dict
        """
        return _clean_dict(self.__dict__)

    def __iter__(self):
        for k, v in self.asdict().items():
            yield k, v


class Stop(object):
    """A bus Stop, identified by a Stop ID. Buses will arrive to it."""
    def __init__(
            self,
            stopid: Union[int, str],
            name: str,
            lat: Union[float, str, None] = None,
            lon: Union[float, str, None] = None,
            other: Optional[Dict] = None
    ):
        """
        :param stopid: Stop ID/Number (required)
        :param name: Stop name (required)
        :param lat: Stop location latitude (optional, default=None)
        :param lon: Stop location longitude (optional, default=None)
        :type stopid: int
        :type name: str
        :type lat: float or None
        :type lon: float or None
        .. note:: StopID, Lat and Lon values will be casted on __init__
        .. note:: Stop Name will be strip on __init__
        .. note:: Lat and Lon are both required
        """
        self.stopid: int = int(stopid)
        # self.id: int = self.stopid
        self.name: str = name.strip()
        self.other: Dict = other if other is not None else dict()
        if lat is None or lon is None:
            self.lat: float = None
            self.lon: float = None
        else:
            self.lat: float = float(lat)
            self.lon: float = float(lon)

    def has_location(self) -> bool:
        """Check if this Stop has a valid location set (latitude and longitude).
        :return: True if Stop has both Latitude & Longitude values, False if one or both are missing
        :rtype: bool
        """
        return not (self.lat, self.lon) == (None, None)

    def asdict(self):
        """Return all the data available about this Stop as a dict.
        Parameters where values are None will be hidden.
        :return: all parameters of this Stop object as a dict
        :rtype: dict
        """
        return _clean_dict(self.__dict__)

    def __iter__(self):
        for k, v in self.asdict().items():
            yield k, v


# https://docs.python.org/3/library/typing.html#newtype
# StopGetterClassVar = ClassVar[Callable[[int], Stop]]
StopGetter = NewType("StopGetter", Callable[[int], Stop])
StopSetter = NewType("StopSetter", Callable[[Stop], None])
StopDeleter = NewType("StopDeleter", Callable[[int], bool])
BusGetter = NewType("BusGetter", Callable[[int], List[Bus]])
BusSetter = NewType("BusSetter", Callable)
BusDeleter = NewType("BusDeleter", Callable)


def _clean_dict(d) -> Dict:
    """Remove null (None) elements from a dictionary.
    :param d: original dict to analyze
    :type d: dict
    :return: copy of d, but keys with null values are removed
    :rtype: dict
    """
    dc = d.copy()
    for k, v in d.items():
        if v is None:
            dc.pop(k)
    return dc
