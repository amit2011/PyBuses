
from math import sin, cos, sqrt, atan2, radians

# Punto Central
lat1=42.2322022750622
lon1=-8.70379224637247

# Punto Parada
lat2=42.2312737858673
lon2=-8.70014564481647

# approximate radius of earth in km
R = 6373.0

lat1 = radians(lat1)
lon1 = radians(lon1)
lat2 = radians(lat2)
lon2 = radians(lon2)

dlon = lon2 - lon1
dlat = lat2 - lat1

a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
c = 2 * atan2(sqrt(a), sqrt(1 - a))

distance = R * c

print(distance, "km")
print(distance*1000, "m")


# from math import radians, cos, sin, asin, sqrt
#
#
# def haversine(lon1, lat1, lon2, lat2):
#     """
#     Calculate the great circle distance between two points
#     on the earth (specified in decimal degrees)
#     """
#     # convert decimal degrees to radians
#     lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
#
#     # haversine formula
#     dlon = lon2 - lon1
#     dlat = lat2 - lat1
#     a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
#     c = 2 * asin(sqrt(a))
#     r = 6371  # Radius of earth in kilometers. Use 3956 for miles
#     return c * r
#
#
# # Punto de búsqueda
# center_point = [{'lat': 42.2322022750622, 'lng': -8.70379224637247}]
# # Comprobar si parada está dentro del círculo
# test_point = [{'lat': 42.2334129399705, 'lng': -8.72904515586103}]
#
# lat1 = center_point[0]['lat']
# lon1 = center_point[0]['lng']
# lat2 = test_point[0]['lat']
# lon2 = test_point[0]['lng']
#
# radius = 1.00  # in kilometer
#
# h = haversine(lon1, lat1, lon2, lat2)
#
# print('Distance (km) : ', h)
# if h <= radius:
#     print('Inside the area')
# else:
#     print('Outside the area')
