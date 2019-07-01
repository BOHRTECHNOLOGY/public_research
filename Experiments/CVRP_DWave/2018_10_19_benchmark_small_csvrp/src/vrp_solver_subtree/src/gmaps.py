'''
Simple Google Maps Client wrapper.
Provides required data and hides other 
stuff like security, keys, etc.

Google Maps API Client from `googlemaps` package was used.
For more details see: `https://github.com/googlemaps/google-maps-services-python`
'''

import requests
import argparse
import numpy as np
import googlemaps
import os


class GMaps:
    path_key = 'gmaps_credentials.txt'
    api_key = None

    def __init__(self, offline=False):
        '''
        Initialize GMaps object. Read API key.
        `offline` arg can be set to True if you want to test 
        code using this object.
        '''
        self.lang = 'polish'
        self.region = 'pl'
        self.offline = offline
        abs_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(abs_path, self.path_key), 'r') as f:
            self.api_key = f.read()
        self.client = googlemaps.Client(key=self.api_key)


    def get_location(self, addr):
        '''
        Do the request to GMaps and extract latitude and longitude
        of given place.
        Args:
            addr: requested address
        Returns:
            latitude, longitude, formatted address
        '''
        print('Requesting geolocation of: ', addr)

        if self.offline:
            print('Warning! GMaps is using in OFFLINE mode! Random data is generated!')
            return np.random.uniform(-90, 90), np.random.uniform(-180, 180), '00-000'

        result = self.client.geocode(addr, language=self.lang, region=self.region)
        result = result[0]
        lat = result['geometry']['location']['lat']
        lng = result['geometry']['location']['lng']
        fmt_addr = result['formatted_address']
        return lat, lng, fmt_addr 


    def get_address(self, lat, lng):
        '''
        Do the reverse geocode request to GMaps.
        Given latitude and longitude find address.
        Args:
            lat: latitude
            lng: longitude
        Returns:
            Address
        '''
        print('Requesting geolocation of: {}, {}'.format(lat, lng))

        if self.offline:
            print('Warning! GMaps is using in OFFLINE mode! Fake data is generated!')
            return 'ul. XXX, 00-000 XXX'

        result = self.client.reverse_geocode((lat, lng), language=self.lang)
        result = result[0]
        fmt_addr = result['formatted_address']
        return fmt_addr 


    def get_distance(self, addr_a, addr_b, mode='driving'):
        '''
        Get distance and estimated travel time from point A to point B.
        Default mode is driving.
        
        Args:
            addr_a: start address
            addr_b: destination address
            mode: (default) `driving`

        Returns:
            Tuple of:
            - distance in km
            - estimated time in mins, 
            - list of route's steps as:
              - start (lat, lng)
              - end (lat, lng)
              - distance in km
              - duration in mins
        '''
        print('Requesting directions:\nfrom: %s\nto: %s' % (addr_a, addr_b))

        if self.offline:
            print('Warning! GMaps is using in OFFLINE mode! Random data is generated!')
            return np.random.uniform(1, 50), np.random.uniform(5, 60), []

        result = self.client.directions(addr_a, addr_b, mode=mode, language=self.lang)
        result = result[0]
        route = result['legs'][0]
        distance = route['distance']['value'] / 1000.
        T = route['duration']['value'] / 60.
        way = []
        for step in route['steps']:
            step_start = step['start_location']
            step_end = step['end_location']
            step_dist = step['distance']['value'] / 1000.
            step_dur = step['duration']['value'] / 60.
            way.append((
                (step_start['lat'], step_start['lng']),
                (step_end['lat'], step_end['lng']),
                step_dist,
                step_dur))
        return distance, T, way


if __name__ == "__main__":
    # GMaps service cli frontend for tests and quickchecks.
    # Usage: `python gmaps.py --loc <addr> --dir <start addr> <end addr>`

    parser = argparse.ArgumentParser(description='Google Maps requests.')
    parser.add_argument('--loc', metavar='ADDR', 
        help='Find latitude and longitude of given address.')
    parser.add_argument('--addr', nargs=2, metavar=('LAT', 'LNG'),
        help='Find address of point given as pair (lat, lng).')
    parser.add_argument('--route', metavar=('A', 'B'), nargs=2, 
        help='Directions from address A to address B')
    args = parser.parse_args()
    
    gmaps = GMaps()
    if args.loc is not None:
        lat, lng, addr = gmaps.get_location(args.loc)
        print("Latitude: {}\nLongitude: {}\nAddress: {}".format(lat, lng, addr))
        
    if args.addr is not None:
        addr = gmaps.get_address(*args.addr)
        print("Address: {}".format(addr))

    if args.route is not None:
        km, t, route = gmaps.get_distance(args.route[0], args.route[1])
        print('Distance: %.1f km, Estimated time: %.1f m' % (km, t))
        print('Route: ')
        for (s_lat, s_lng), (e_lat, e_lng), dist, dur in route:
            print('from: (%f, %f), to: (%f, %f), dist: %f, duration: %f' % (
                s_lat, s_lng, e_lat, e_lng, dist, dur))

