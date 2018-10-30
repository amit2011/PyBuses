
# Native modules
from typing import Optional, List  # Python => 3.5
from collections import namedtuple
from threading import Thread, Lock
# Own modules
from .exceptions import *
from .assets import *

__all__ = ["PyBuses"]

"""Bus Sorting Methods are ints, but can be used with alias from the BusSortMethods named tuple.
NONE = 0
TIME = 1
LINE = 2
ROUTE = 3
"""
_bus_sort_methods_namedtuple = namedtuple("BusSortMethods", ["NONE", "TIME", "LINE", "ROUTE"])
BusSortMethods = _bus_sort_methods_namedtuple(0, 1, 2, 3)


class PyBuses(object):
    """A PyBuses object to help managing bus stops and look for incoming buses.
    This object should be threated as a concrete transport service, i.e.:
        - "the bus service of King's Landing"
        - "the metro service of Liberty City"
        - "the train service of Hamburg"
        - "the bus service of Hamburg"
    Each one of these services would have a PyBuses object, with their getters, setters and deleters.

    Getters are custom, required functions that fetch Stop info and Bus lists from certain sources.
    At least one Stop Getter and one Bus Getter are required to fetch stops and buses respectively.

    Setters are custom, optional functions, that will save found Stops or list of buses to custom destinations
    (i.e. a database, local variables, a file, cache...)
    Setters are supposed to be executed after a Stop or Bus query is successful.
    However, PyBuses will not do it automatically.

    Deleters are custom, optional functions, that will delete saved Stops or list of buses on custom destinations,
    usually the same places as Setters.

    The PyBuses methods that use these functions are:
        - Stop Getters: find_stop()
        - Stop Setters: save_stop()
        - Stop Deleters: delete_stop()
        - Bus Getters: get_buses()
        - Bus Setters: save_buses()
        - Bus Deleters: delete_buses()

    Please refer to documentation in order to check how Getter, Setter and Deleter functions must work.
    """

    def __init__(
            self,
            stop_getters: Optional[List[StopGetter]] = None,
            stop_setters: Optional[List[StopSetter]] = None,
            stop_deleters: Optional[List[StopDeleter]] = None,
            bus_getters: Optional[List[BusGetter]] = None,
            bus_setters: Optional[List[BusSetter]] = None,
            bus_deleters: Optional[List[BusDeleter]] = None,
            use_all_stop_setters: bool = False,
            use_all_bus_setters: bool = False,
            use_all_stop_deleters: bool = True,
            use_all_bus_deleters: bool = True,
    ):
        """
        :param stop_getters: List of Stop getters functions
        :param stop_setters: List of Stop setters functions
        :param bus_getters: List of Bus getters functions
        :param bus_setters: List of Bus setters functions
        :param use_all_stop_setters: if True, use all the defined Stop Setters when saving a Stop (default=False)
        :param use_all_bus_setters: if True, use all the defined Bus Setters when saving a Bus (default=False)
        :param use_all_stop_deleters: if True, use all the defined Stop Deleters when deleting a Stop (default=True)
        :param use_all_bus_deleters: if True, use all the defined Bus Deleters when deleting a Bus (default=True)
        :type stop_getters: list or None
        :type stop_setters: list or None
        :type stop_deleters: list or None
        :type bus_getters: list or None
        :type bus_setters: list or None
        :type stop_deleters: list or None
        :type use_all_stop_setters: bool
        :type use_all_bus_setters: bool
        :type use_all_stop_deleters: bool
        :type use_all_bus_deleters: bool
        """
        self.stop_getters: List[StopGetter] = list() if stop_getters is None else list(stop_getters)
        self.stop_setters: List[StopSetter] = list() if stop_setters is None else list(stop_setters)
        self.stop_deleters: List[StopDeleter] = list() if stop_deleters is None else list(stop_deleters)
        self.bus_getters: List[BusGetter] = list() if bus_getters is None else list(bus_getters)
        self.bus_setters: List[BusSetter] = list() if bus_setters is None else list(bus_setters)
        self.bus_deleters: List[BusDeleter] = list() if bus_deleters is None else list(bus_deleters)
        self.use_all_stop_setters: bool = use_all_stop_setters
        self.use_all_bus_setters: bool = use_all_bus_setters
        self.use_all_stop_deleters: bool = use_all_stop_deleters
        self.use_all_bus_deleters: bool = use_all_bus_deleters

    def find_stop(self, stopid: int, online: bool = False) -> Stop:
        """Find a Stop using the defined Stop Getters on this PyBuses instances.
        If no Getters are defined, MissingGetters exception is raised.
        :param stopid: ID of the Stop to find
        :param online: if True, only search on Online Getters (default=False)
        :type stopid: int
        :type online: bool
        :return: Stop object
        :rtype: list of Stop or False or Exception
        :raise: MissingGetters or StopNotFound or StopGetterUnavailable
        """
        getters: List[StopGetter] = self.get_stop_getters(online)
        if not getters:
            raise MissingGetters("No Stop getters defined on this PyBuses instance")
        for getter in getters:  # type: StopGetter
            try:
                return getter(stopid)
            except StopGetterUnavailable:
                continue
        raise StopGetterUnavailable("Stop info could not be retrieved for any of the Stop getters defined")

    def save_stop(self, stop: Stop, update: bool = True, use_all_stop_setters: Optional[bool] = None):
        """Save the provided Stop object on the Stop setters defined.
        The stop will only be saved on the first Setter where the Stop was saved successfully,
        unless use_all_stop_setters attribute of PyBuses class or on this method is True.
        If no Setters are defined, MissingSetters exception is raised.
        If any of the Stop setters worked, StopSetterUnavailable exception is raised.
        :param stop: Stop object to save
        :param update: if True, when the Stop currently exists on a Setter data destination,
                       update stop on destination with the current data of the Stop provided (default=True)
        :param use_all_stop_setters: if True, save the Stop on all the Stop Setters
               (default=use the value declared on this PyBuses instance)
        :type stop: Stop
        :type update: bool
        :type use_all_stop_setters: bool or None
        :raise: MissingSetters or StopSetterUnavailable
        """
        setters: List[StopSetter] = self.get_stop_setters()
        if not setters:
            raise MissingSetters("No Stop setters defined on this PyBuses instance")
        success = False
        if use_all_stop_setters is None:
            use_all_stop_setters = self.use_all_stop_setters
        for setter in setters:  # type: StopSetter
            try:
                setter(stop, update=update)
            except StopSetterUnavailable:
                continue
            else:
                success = True
                if not use_all_stop_setters:
                    break
        if not success:
            raise StopSetterUnavailable("Stop could not be saved on any of the Stop setters defined")

    def delete_stop(self, stopid: int):
        """Delete the stop that matches the given Stop ID using the defined Stop Deleters.
        The stop will only be deleted on the first Deleter where the Stop was deleted successfully,
        unless use_all_stop_deleters attribute of PyBuses class is True (which is by default).
        No exceptions will be raised if the stop was not deleted because it was not registered.
        Only when all the Deleters themselves failed, StopDeleterUnavailable will be raised.
        If no Deleters are defined, MissingDeleters exception is raised.
        :param stopid: Stop ID of the Stop to delete
        :type stopid: int
        :raise: MissingDeleters or StopDeleterUnavailable
        """
        deleters: List[StopDeleter] = self.get_stop_deleters()
        if not deleters:
            raise MissingDeleters("No Stop deleters defined on this PyBuses instance")
        success = False
        for deleter in deleters:  # type: StopDeleter
            try:
                deleter(stopid)
            except StopDeleterUnavailable:
                continue
            else:
                success = True
                if not self.use_all_stop_deleters:
                    break
        if not success:
            raise StopDeleterUnavailable("Stop could not be deleted with any of the Stop deleters defined")

    def find_all_stops(
            self,
            end: int,
            start: int = 1,
            threads: int = 0,
            update: bool = True,
            use_all_stop_getters: bool = False,
            use_all_stop_setters: Optional[bool] = None
    ):
        """Find all the stops when the online resources do not provide a full list of Stops.
        This method will manually search the Stops by ID sequentially
        between the start and end ranges using the available Stop Getters.
        The method can run on the background using thread.
        The threads parameter define how many threads will be used. By default is 0, which means use no threads.
        All the found stops will be saved/updated using the Stop setters defined on the PyBuses instance.
        :param end: Stop ID limit to search
        :param start: First Stop ID to search (default=1)
        :param threads: number of threads to use (default=0: use no threads)
        :param update: if True, when a found Stop currently exists on a Setter data destination,
                       update stop on destination with the current data of the Stop provided (default=True)
        :param use_all_stop_getters: if True, ignore the StopNotExist/StopNotFound exceptions
                                     and keep searching on next getters (default=False)
        :param use_all_stop_setters: if True, save each Stop on all the Stop Setters
                                     (default=use the value declared on this PyBuses instance)
        :type end: int
        :type start: int
        :type threads: int
        :type update: bool
        :type use_all_stop_getters: bool
        :type use_all_stop_setters: bool or None
        :return: List[Stop] or None
        :raise: MissingGetters or MissingSetters
        """
        getters: List[StopGetter] = self.get_stop_getters(True)  # Get all Online getters
        if not getters:
            raise MissingGetters("No Stop getters defined on this PyBuses instance")
        if not self.get_stop_setters():
            raise MissingSetters("No Stop setters defined on this PyBuses instance")

        def _find_stop_and_save(stopid_tofind):  # Function used by threads/no-thread
            for getter in getters:  # type: StopGetter
                try:
                    print("Searching Stop", stopid_tofind)
                    stop = getter(stopid_tofind)
                except StopGetterUnavailable:
                    continue
                except (StopNotFound, StopNotExist):
                    if use_all_stop_getters:
                        continue
                    else:
                        break
                else:
                    try:
                        print(f"Stop {stop.stopid} found! Name={stop.name}, lat={stop.lat}, lon={stop.lon}")
                        self.save_stop(stop, update=update, use_all_stop_setters=use_all_stop_setters)
                    except StopSetterUnavailable:
                        pass

        if threads <= 0:  # Use no threads
            for stopid in range(start, end+1):
                _find_stop_and_save(stopid)
        else:  # Use threads
            # created_threads = list()

            class Counter(object):
                def __init__(self, initial, limit):
                    self.value: int = initial
                    self.limit: int = limit
                    self.lock = Lock()

                def get(self):
                    self.lock.acquire()
                    current = self.value
                    if current > self.limit:
                        self.lock.release()
                        raise IndexError()
                    self.value += 1
                    self.lock.release()
                    return current

            counter = Counter(initial=start, limit=end)

            def _thread_f(th_counter: Counter):  # Function for threads
                while True:
                    try:
                        stopid_tofind = th_counter.get()
                    except IndexError:
                        break
                    else:
                        _find_stop_and_save(stopid_tofind)

            for i in range(threads):
                th = Thread(target=_thread_f, args=(counter,))
                # created_threads.append(th)
                th.start()

    def get_buses(self, stopid: int, sort_by: Optional[int] = BusSortMethods.TIME, reverse: bool = False) -> List[Bus]:
        """Get a live list of all the Buses coming to a certain Stop and the remaining until arrival.
        If no Getters are defined, MissingGetters exception is raised.
        :param stopid: ID of the Stop to search buses on
        :param sort_by: method used to sort buses (use constants available in PyBuses (default=TIME: sort by Time)
        :param reverse: if True, reverse sort the buses (default=False)
        :type stopid: int
        :type sort_by: int or None
        :type reverse: bool
        :return: List of Buses
        :rtype: List[Bus]
        :raise: MissingGetters or StopNotFound or BusGetterUnavailable
        """
        getters: List[BusGetter] = self.get_bus_getters()
        if not getters:
            raise MissingGetters("No Bus getters defined on this PyBuses instance")
        for getter in getters:  # type: BusGetter
            try:
                buses: List[Bus] = getter(stopid)
                if sort_by == BusSortMethods.TIME:
                    buses.sort(key=lambda x: x.time, reverse=reverse)
                elif sort_by == BusSortMethods.LINE:
                    buses.sort(key=lambda x: x.line, reverse=reverse)
                elif sort_by == BusSortMethods.ROUTE:
                    buses.sort(key=lambda x: x.route, reverse=reverse)
                return buses
            except BusGetterUnavailable:
                continue
        raise BusGetterUnavailable("Bus list could not be retrieved with any of the Bus getters defined")

    def save_buses(self):
        pass

    def delete_buses(self):
        pass

    def add_stop_getter(self, f: StopGetter, online: bool = False):
        try:
            f.online = online
        except AttributeError:
            pass
        # TOFIX Los métodos no pueden llevar atributos, por lo que hay que buscar otra forma de definir el online
        self.stop_getters.append(f)

    def add_stop_setter(self, f: StopSetter):
        self.stop_setters.append(f)

    def add_bus_getter(self, f: BusGetter):
        self.bus_getters.append(f)

    def add_bus_setter(self, f: BusSetter):
        self.bus_setters.append(f)

    def add_bus_deleter(self, f: BusDeleter):
        self.bus_deleters.append(f)

    def get_stop_getters(self, online: bool = False) -> List[StopGetter]:
        if online:
            return [
                g for g in self.stop_getters
                if "online" in g.__dict__.keys()  # Avoid AttributeError when getter does not have the attribute defined
                   and g.online is True
            ]
        else:
            return self.stop_getters

    def get_stop_setters(self) -> List[StopSetter]:
        return self.stop_setters

    def get_stop_deleters(self) -> List[StopDeleter]:
        return self.stop_deleters

    def get_bus_getters(self) -> List[BusGetter]:
        return self.bus_getters

    def get_bus_setters(self) -> List[BusSetter]:
        return self.bus_setters

    def get_bus_deleters(self) -> List[BusDeleter]:
        return self.bus_deleters

# class PyBusesOld(object):
#     """A PyBuses object that will help organizing bus stops and lookup incoming buses.
#     Object must be initialized with a list of Stop and Bus getter functions,
#     which must interact with the online server that provides Stop info and Buses.
#     """
#
#     def __init__(self, stop_getters, bus_getters, db_name="Databases/Stops.sqlite"):
#         """A PyBuses object, associated with a city/bus service using stop and bus getters.
#         :param stop_getters: a single or list of functions to get info of a stop
#         :param bus_getters: a single or list of functions to get buses coming to a stop
#         :param db_name: name (relative route) of SQLite database where Stop info will be stored
#         """
#         # Create cache and database for stops
#         self.stops_cache = StopsCache()
#         self.db = Database(db_name)
#         self.stopsdb = StopsDatabase(self.db)
#
#         # Set Stop getters
#         self._native_stop_getters = (self.stops_cache.find_stop_cache, self.stopsdb.find_stop)
#         self.stop_getters = list(self._native_stop_getters)
#         if type(stop_getters) not in (list, tuple):
#             stop_getters = (stop_getters,)
#         self.stop_getters.extend(stop_getters)  # Add custom getters to stop getters list
#
#         # Set Bus getters
#         self.bus_getters = []
#         if type(bus_getters) not in (list, tuple):
#             bus_getters = (bus_getters,)
#         self.bus_getters.extend(bus_getters)
#
#         # Stops Cache - start cleanup service (thread)
#         self.stops_cache.start_cleanup_service(age=215)
#
#         # Google StreetView/Maps objects
#         self.streetview = GoogleStreetView(self.db)
#         self.maps = GoogleMaps(self.db)
#
#         # Debug everything:
#         # log.info("Created a PyBuses stops with the getters from {module}:\n* Stop getters: {stopgg}\n* Bus getters: {busgg}".format(
#         #     stopgg=str(tuple(f.__name__ for f in self.stop_getters)),
#         #     busgg=str(tuple(f.__name__ for f in self.bus_getters))
#         # ))
#         logmsg = "Created a PyBuses stops with the following getters:"
#         for getter in (self.stop_getters + self.bus_getters):
#             logmsg += "\n    [{type}] {name} from {module}".format(
#                 type="Stop" if getter in self.stop_getters else "Bus",
#                 name=getter.__name__,
#                 module=getter.__module__
#             )
#         # log.debug(logmsg)
#
#     class StopNotFound(Exception):
#         """This will be raised when a stop isn't found from find_stop methods
#         (which means a Stop getter replied that stop doesn't exist)
#         """
#         pass
#
#     def find_stop(self, stopid):
#         """Find a Stop by the StopID using all the getters designed on the PyBuses object,
#         plus the native Cache and DB getters.
#         :param stopid: StopID to find (int)
#         :return: Stop object is stop is found
#         :raises: self.StopNotFound if any of the non-native getters reported stop as non-existent
#         :raises: ConnectionError if stop could not be fetched from any of the getters (i.e. network problems)
#         """
#         # log.info("Searching for Stop #{}".format(stopid))
#         for getter in self.stop_getters:
#             # log.debug("Searching Stop #{stopid} with getter {getter}@{gmodule}".format(
#             #     stopid=stopid,
#             #     getter=getter.__name__,
#             #     gmodule=getter.__module__
#             # ))
#             result = getter(stopid=stopid)
#             if result and result.name is not None:  # Stop found
#                 # log.info("Stop #{stopid} (Name={stopname}) found by getter {getter}@{gmodule}".format(
#                 #     stopid=stopid,
#                 #     stopname=result.name,
#                 #     getter=getter.__name__,
#                 #     gmodule=getter.__module__
#                 # ))
#                 if getter not in self._native_stop_getters or getter != self.stops_cache.find_stop_cache:
#                     # log.info("Saving Stop #{} in local cache".format(stopid))
#                     self.save_stop_cache(result) # Save stop in local cache if it wasn't cached
#                 elif getter not in self._native_stop_getters:
#                     # log.info("Saving Stop #{} in DB".format(stopid))
#                     self.save_stop_db(result) # Save stop in DB if it wasn't in DB
#                 return result
#             if result is False:  # Stop not found
#                 # log.debug("Stop #{} identified as Not Found/Unexistent".format(stopid))
#                 raise self.StopNotFound("Stop {} not found!".format(stopid))
#             # If error (result is None): keep trying other getters
#         # Raise error if couldn't retrieve Stop info from any of the getters
#         # log.warning("Could not retrieve Stop #{} info from any of the getters available (this doesn't know the stop doesn't exist)".format(stopid))
#         raise ConnectionError("Could not retrieve Stop #{} info from any of the getters".format(stopid))
#
#     def get_buses(self, stopid):
#         # log.info("Getting buses for Stop #{}".format(stopid))
#         for getter in self.bus_getters:
#             result = getter(stopid=stopid)
#             if type(result) is list:
#                 result.sort(key=lambda x: x.time) #Sort buses by time
#                 # log.info("Found {nbuses} buses for Stop #{stopid} with the getter {getter}@{gmodule}".format(
#                 #     nbuses=len(result),
#                 #     stopid=stopid,
#                 #     getter=getter.__name__,
#                 #     gmodule=getter.__module__
#                 # ))
#                 return result
#             # If error: keep trying other getters
#         # Raise error if couldn't retrieve Bus list from any of the getters
#         # log.warning("Could not retrieve buses for Stop #{} from any of the getters available".format(stopid))
#         raise ConnectionError("Could not retrieve buses for Stop #{} from any of the getters".format(stopid))
#
#     def save_stop_db(self, stop):
#         self.stopsdb.save_stop(stop)
#
#     def update_stop_db(self, stop):
#         self.stopsdb.save_stop(stop, update=True)
#
#     def save_stop_cache(self, stop):
#         self.stops_cache.save_stop_cache(stop)
#
#     # def get_streetview(self, stop):
#     #     """Get a Google StreetView image for the desired stop.
#     #     :param stop: Stop object
#     #     :return: Image as bytes object or string with Telegram File ID
#     #     """
#     #     return self.streetview.get_streetview(stop)
#
#     # def save_streetview(self, stopid, fileid):
#     #     """Save a Google StreetView image on local DB, given the Telegram File ID
#     #     :param stopid: Stop ID of the stop to save
#     #     :param fileid: Telegram File ID
#     #     """
#     #     self.streetview.save_streetview_db(stopid, fileid)
#
#     # def get_maps(self, stop, vertical=True, terrain=False):
#     #     """
#     #     """
#     #     return self.maps.get_maps(stop, vertical, terrain)
#
#     # def save_maps(self, stopid, fileid, vertical, terrain):
#     #     self.maps.save_maps_db(stopid, fileid, vertical, terrain)
