# PyBuses

**_This project is still Work in Progress._**
_Things may change until the first production version._

PyBuses is a Python framework that helps working with buses and bus stops,
but it can be used with any other public transport such as trains, boats, metro...

The framework works with two basic assets:

* Buses: moving vehicles that arrive to Stops
* Stops: where people wait for buses, and buses arrive

The original idea is to fetch a realtime list of all the buses coming to a certain stop, with the time remaining until
  arrival, that users can see on apps, webapps, Telegram bots...

Additionally, PyBuses can:

* Manage Stops (save, search, list, delete)
* Show the available bus lines and routes
* Search stops near a given location
* Usage of Google Maps & Google StreetView to get real map & screenshots of the stops (based on location) 

Please, notice that along all the documentation and code, transport vehicles are threated as "Bus",
but they can be of mostly any other type.

## a) Requirements

* Python 3.7
* requests
* pymongo

## b) Assets

### b.1) Stops

Stops are physical locations where buses arrive to pick up passengers.
They must have a unique identifier (stopid) and a name.
They can have their geographic location through coordinates (latitude & longitude).

#### Attributes

* stopid - unique Stop Identifier (required, int)
* name - human-readable Stop Name (required, string)
* lat - location of this stop: Latitude (optional, float)
* lon - location of this stop: Longitude (optional, float)
* other - additional information of this Stop (optional, dict)

### b.2) Buses

Buses are moving vehicles that arrive and stop at Stops to pick up passengers.
For each stop, it's known what buses will arrive and the time remaining until arrival.

Buses are also referenced for the Static Bus search, which is used to
serve information about all the available bus lines and routes on the city.

#### Attributes

* line - Bus line (required, str)
* route - Bus route (required, str)
* time - minutes remaining for the bus to arrive at a certain stop (optional, int or float)
* distance - how far away is the bus from a certain stop (optional, int or float)
* other - additional information of this Bus (optional, dict)

## c) Getters, Setters and Deleters

On PyBuses, Getters, Setters and Deleters are custom functions defined outside PyBuses
to work with the data required by the framework.

Examples of Getters include retrieving Stop info or realtime Buses arriving to a Stop, using an external API.
Examples of Setters include saving Stop data (id, name, location) to a database.

At least one Stop Getter is required to retrieve Stop info,
and one Bus Getter is required to get the buses arriving to a stop.

The setters usually write data where getters read it later on from.
For example, a Stop setter can save a Stop on a MySQL database, and a Stop getter can find that stop on that database.
However, the operation of saving a Stop found by a getter on a setter is not automatically performed by PyBuses.

The deleters are functions that remove data previously registered by a setter.

### c.1) Stop functions

Stop functions get Stop data from any source available, 
i.e. online sources such as APIs, offline sources like local databases...

#### c.1.i) Stop getters

* Stop Getters should connect to a valid data source to fetch the stop info from.
* Stop Getters receive as parameter the Stop ID of the Stop to search, as int.
* If a Stop is found, the getter must return a valid PyBuses Stop data object, with all the available info completed
  (at least stopid and stop name).
* If a Stop is not found, but it might exist (i.e. is not registered in our database but could be on a remote API),
the getter must raise the StopNotFound() exception.
* If a Stop is not found, and the getter is really sure about that stop does not physically exist,
  it must raise the StopNotExist() exception.
* If the data source is not available or have some problems or errors,
  the getter must throw the StopGetterUnavailable() exception.

```python  

```

#### c.1.ii) Stop setters

* Stop Setters save an existing Stop to a local or controlled storage, such as a database.
* The objectives of Stop setters are:
    * Avoid sending requests to an external API if not neccesary.
    * Allow users to search stops by name or location, which is faster with a local getter than asking a remote API.
* Stop Setters receive as parameter a Stop object of PyBuses, with all the available information of the stop.
* Stop Setters return nothing when an operation was successful.
* If some error happened when saving the stop using a Setter, or the resource is not available,
  the setter must throw the StopSetterUnavailable() exception.

```python

```

#### c.1.iii) Stop deleters

* Stop Deleters delete an existing stop saved on a local or controlled storage, usually stored by a getter beforehand.
* Deleters receive as parameter the Stop ID of the Stop to delete.
* If the Stop was deleted, the Deleter must return True.
* If the Stop was not deleted, most probably because it was not registered on the data storage,
  the Deleter must return False.
* If some error happened when deleting the stop using a Deleter, or the resource is not available,
  the deleter must throw the StopDeleterUnavailable() exception.

```python

```

### c.2) User-saved Stops functions

(User-saved Stops managed by PyBuses or Telegram Bot framework?) 

#### c.2.i) User-saved Stops getters



#### c.2.ii) User-saved Stops setters



#### c.2.iii) User-saved Stops deleters



### c.3) Bus functions

Bus functions must work with dynamic buses that come to a certain stop, having a known remaining time until arrival.
Bus Setters are mostly optional, and more focused on having some sort of cache.

#### c.3.i) Bus getters

* Bus getters usually connect to an API to retrieve the list of buses arriving to a Stop, in real time.
* A bus getter can be called, for example, when a user wants to get the bus schedule for a certain stop.
* Bus getters receive as parameter the Stop ID of the Stop to get the buses of, as int.
* If buses are found, a list of Bus objects is returned.
* The getter does not have to sort the buses by time or any other desired parameter. They get sorted by PyBuses.
* If no buses are found, but nothing was wrong, an empty list is returned.
* If the Stop does not exist, the setter must throw the StopNotFound() exception.
* If some error happened when fetching the list of buses, the getter must throw the BusGetterUnavailable() exception.

#### c.3.ii) Bus setters



### c.4) Static Bus functions



#### c.4.i) Static Bus getters



#### c.4.ii) Static Bus setters



#### c.4.ii) Static Bus deleters


## d) The PyBuses object

Any public transport service that will be managed with PyBuses must use one instance of the PyBuses object.
This object should be threated as a concrete transport service, i.e.:
- "the bus service of King's Landing"
- "the metro service of Liberty City"
- "the train service of Hamburg"
- "the bus service of Hamburg"
Each one of these services would have a PyBuses object, with their getters, setters and deleters.


