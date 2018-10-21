
# Native libraries
import atexit
import time
import traceback
from typing import Union, Optional
# Installed libraries
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
# Own modules
from .assets import Stop, StopGetter, StopSetter, StopDeleter
from .exceptions import *

"""STRUCTURE OF MongoDB DATABASE used by PyBuses
The database only helds Stop data, including Google Maps & StreetView related data

Database: pybuses
Collection: stops

Structure of documents (fields with * are optional, so they can be missing on certain stops)
{
    "_id": 1234,
    "name": "123 Fake St.",
    "saved": <dt>
    "updated": <dt>
    "lat": 1.23456, *
    "lon": -1.23456 *
}
```
Stop ID is used as the Document ID of MongoDB.
<dt> are ints with the timestamp when Stop was saved for first time and updated for last time.
Timestamps are saved on Unix/Epoch format, and UTC timezone.
"""
# TODO add GoogleMaps & StreetView data to stop documents

# http://api.mongodb.com/python/current/tutorial.html

__all__ = [
    "MongoDB", "DEFAULT_TIMEOUT", "DEFAULT_DATABASE_NAME", "DEFAULT_DATABASE_COLLECTION",
    "PyMongoError", "MongoDBUnavailable"
]

DEFAULT_TIMEOUT = 1
DEFAULT_DATABASE_NAME = "pybuses"
DEFAULT_DATABASE_COLLECTION = "stops"


class MongoDB(object):
    def __init__(
            self,
            host: str = "localhost",
            port: int = 27017,
            uri: Optional[str] = None,
            timeout: Union[int, float] = DEFAULT_TIMEOUT,
            db_name: str = DEFAULT_DATABASE_NAME,
            stops_collection_name: str = DEFAULT_DATABASE_COLLECTION
    ):
        """Location of the server must be given using host and port parameters, or uri.
        If URI is provided, host and port parameters will be ignored.
        A connection with the database will be performed automatically, if possible.
        Otherwise, connect method must be called after declaring correct server info (host+port/URI).
        :param host: Host where MongoDB server is hosted (default="localhost")
        :param port: Port of the MongoDB server (default=27017)
        :param uri: URI of the server, instead of host and port (default=None)
        :param timeout: Timeout for MongoDB operations in seconds (default=10)
        :param db_name: Name of the database used by PyBuses (default="pybuses")
        :param stops_collection_name: Name of the db collection used for the stops
        :type host: str
        :type port: int
        :type uri: str or None
        :type timeout: int or float
        :type db_name: str
        :type stops_collection_name: str
        """
        self.timeout: Union[int, float] = timeout
        self.host: str = host
        self.port: int = port
        self.uri: Optional[str] = uri
        self.db_name: str = db_name
        self.stops_collection_name: str = stops_collection_name
        self.client: MongoClient = None
        self.db: Database = None
        self.collection: Collection = None
        self.documents: Collection = None
        self.find_stop: StopGetter = self.find_stop  # Set StopGetter data type on this embedded getter
        self.save_stop: StopSetter = self.save_stop  # Set StopSetter data type on this embedded setter
        self.delete_stop: StopDeleter = self.delete_stop  # Set StopDeleter data type on this embedded deleter

        try:
            self.connect()
        except PyMongoError:
            self.close()

        @atexit.register
        def atexit_f():
            self.close()

    def connect(self, timeout: Optional[Union[int, float]] = None):
        """Connect to the MongoDB database. MongoClient instance is saved on self.client.
        :param timeout: Timeout for the connect operation. If not set, timeout declared on MongoDB instance will be used
        :type timeout: int or float or None
        :raise: PyMongoError
        """
        if timeout is None:
            timeout = self.timeout
        if self.uri is None:
            self.client = MongoClient(
                host=self.host,
                port=self.port,
                serverSelectionTimeoutMS=int(timeout * 1000)
            )
        else:
            self.client = MongoClient(
                uri=self.uri,
                serverSelectionTimeoutMS=int(timeout * 1000)
            )
        self.db = self.client[self.db_name]
        self.collection = self.db[self.stops_collection_name]
        self.documents = self.collection

    def close(self):
        """Disconnect the MongoDB database.
        If database was already closed, nothing will happen.
        """
        if self.check_client():
            self.client.close()
            self.client = None
            self.db = None
            self.collection = None
            self.documents = None

    def check_client(self, raise_exception: bool = False) -> bool:
        """Check if the client object is initialized.
        A initialized client does not mean that is connected with the MongoDB server: use check_connection to check it.
        :param raise_exception: Raise MongoDBUnavailable exception if client not initialized (default=False)
        :return: True if client initialized, False if not
        :rtype: bool
        :raise: MongoDBUnavailable if raise_exception=True and the MongoDB client is not initialized
        """
        b = isinstance(self.client, MongoClient)
        if raise_exception and not b:
            raise MongoDBUnavailable("Client of MongoDB on this instance has not been initialized yet")
        return b

    def check_connection(self, raise_exception: bool = False) -> bool:
        """Tries to perform a operation on the database, and returns True if it was successful.
        Otherwise, if raise_exception=False, returns True.
        If raise_exception=True, the related PyMongo exception will be raised and must be catched on origin.
        :param raise_exception: if True, don't catch exceptions in this method (default=False)
        :type raise_exception: bool
        :return: True if connection is OK; False if connection is down or could not perform the operation
        :rtype: bool
        :raise: PyMongoError if raise_exception=True
        """
        def _f():
            self.client.admin.command("ismaster")
        if not self.check_client():
            return False
        if raise_exception:
            _f()
        else:
            try:
                _f()
            except PyMongoError:
                return False
            else:
                return True

    def find_stop(self, stopid: int) -> Stop:
        """Search a Stop on MongoDB database by the StopID.
        This method is used as a StopGetter function of PyBuses.
        :param stopid: ID of the Stop to search
        :type stopid: int
        :return: found Stop object
        :rtype: Stop
        :raise: StopNotFound or StopGetterUnavailable
        """
        try:
            self.check_client(True)
            result = self.documents.find_one({"_id": stopid})
        except PyMongoError:
            raise StopGetterUnavailable(
                f"Error while searching for Stop {stopid} on MongoDB:\n{traceback.format_exc()}"
            )
            # QUESTION keep traceback?
        if isinstance(result, dict):
            return dict_to_stop(result)
        else:
            raise StopNotFound(f"Stop {stopid} not found on MongoDB database")

    def is_stop_saved(self, stopid: int) -> bool:
        """Check if the given Stop is saved on the database.
        :param stopid: ID of the Stop to search
        :type stopid: int
        :return: True if Stop is saved, False if not found on database
        :rtype: bool
        :raise: PyMongoError or MongoDBNotAvailable
        """
        self.check_client(True)
        return bool(self.documents.find_one({"_id": stopid}))

    def save_stop(self, stop: Stop, update: bool = True):
        """Save or update a Stop on this MongoDB.
        If update=True and the stop is currently saved, it will be updated with the Stop provided.
        This method is used as a StopSetter function of PyBuses.
        :param stop:
        :param update: if True, update stop in database with the Stop provided
        :type stop: Stop
        :type update: bool
        :raise: StopSetterUnavailable
        """
        try:
            self.check_client(True)
            exists = self.is_stop_saved(stop.stopid)
            if not exists:
                # Add new Stop
                d = dict()
                d["_id"] = stop.id
                d["name"] = stop.name
                curtime = current_datetime()
                d["saved"] = curtime
                d["updated"] = curtime
                if stop.has_location():
                    d["lat"] = stop.lat
                    d["lon"] = stop.lon
                self.documents.insert_one(d)
            else:
                # Update existing Stop if param update=True
                if not update:
                    return
                d = dict()
                d["updated"] = current_datetime()
                d["name"] = stop.name
                if stop.has_location():
                    d["lat"] = stop.lat
                    d["lon"] = stop.lon
                self.documents.update_one(
                    filter={"_id": stop.stopid},
                    update={"$set": d}
                )
        except PyMongoError:
            raise StopSetterUnavailable(f"Error while saving Stop to MongoDB:\n{traceback.format_exc()}")
            # QUESTION keep traceback?

    def delete_stop(self, stopid: int) -> bool:
        """Delete a saved stop from MongoDB, and return if the stop was deleted or it did not exist in database.
        :param stopid: ID of the Stop to delete
        :type stopid: int
        :return: True if stop was deleted, False if stop was not deleted (most probably because it was not saved)
        :rtype: bool
        :raise: StopDeleterUnavailable
        """
        try:
            self.check_client(True)
            return bool(self.collection.delete_one({"_id": stopid}).deleted_count)
        except PyMongoError:
            raise StopSetterUnavailable(f"Error while deleting Stop from MongoDB:\n{traceback.format_exc()}")
            # QUESTION keep traceback?


def dict_to_stop(dictionary: dict) -> Stop:
    """Convert a dictionary with Stop info to a Stop object.
    The dictionary must have valid Stop info, with at least "_id" and "name" keys.
    :param dictionary: Dictionary given by a Stop query on MongoDB
    :type dictionary: dict
    :return: Stop object
    :rtype: Stop
    """
    ret = Stop(
        stopid=dictionary["_id"],
        name=dictionary["name"]
    )
    if "lat" in dictionary.keys():
        ret.lat = dictionary["lat"]
    if "lon" in dictionary.keys():
        ret.lon = dictionary["lon"]
    return ret


def current_datetime() -> int:
    """Return current datetime in Unix/Epoch format and UTC timezone.
    :return: current Unix/Epoch timestamp in UTC timezone, parsed to int
    :rtype: int
    """
    return int(time.time())
