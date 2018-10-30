
import requests
import json
from pybuses import PyBuses, MongoDB, Stop, StopGetter, StopGetterUnavailable, StopNotExist

db = MongoDB(host="192.168.0.99", db_name="vigobus", stops_collection_name="stops")

# # GETTERS CON API VITRASA

API_URL = "192.168.0.99:55022"
# API_URL = "localhost:5000"


def getter_vitrasa(stopid) -> Stop:
    r = requests.get(f"http://{API_URL}/stop/{stopid}").text
    j = json.loads(r)
    if j["error"]:
        raise StopGetterUnavailable()
    if not j["exists"]:
        raise StopNotExist()
    return Stop(stopid=stopid, name=j["name"], lat=j["lat"], lon=j["lon"])


getter_vitrasa: StopGetter = getter_vitrasa
# getter_vitrasa.online = True  # no hace falta declararlo aquí, se declara al llamar a add_stop_getter
#                                 aunque se podría probar para cuando se pruebe a pasar getter en constructor

# # TESTS


def test_find_all_stops_threaded():
    pybuses.find_all_stops(start=1, end=1000, threads=10)


def test_find_all_stops_nonthreaded():
    pybuses.find_all_stops(start=5800, end=5810, threads=0)


if __name__ == "__main__":
    pybuses = PyBuses()
    pybuses.add_stop_getter(getter_vitrasa, online=True)
    pybuses.add_stop_getter(db.find_stop)
    pybuses.add_stop_setter(db.save_stop)
    # pybuses.add_stop_deleter(db.delete_stop)

    test_find_all_stops_threaded()
    # test_find_all_stops_nonthreaded()
