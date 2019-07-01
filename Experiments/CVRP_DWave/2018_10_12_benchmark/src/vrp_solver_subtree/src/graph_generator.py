import numpy as np
import pandas as pd


def k_lat(lat_zero):
    '''
    Length in meters of a degree of latitude at latitude `lat_zero` on 
    WGS84 spheroid.
    Args:
        lat_zero: latitude in degrees
    Note:
        Equation is an approximation within `lat_zero +/- 0.5` degree.
    '''
    lat_zero = np.deg2rad(lat_zero)
    return 111132.92 - 559.82 * np.cos(2 * lat_zero) + 1.175 \
            * np.cos(4 * lat_zero) - 0.0023 * np.cos(6 * lat_zero)


def k_long(lat_zero):
    '''
    Length in meters of a degree of longitude at latitude `lat_zero` on 
    WGS84 spheroid.
    Args:
        lat_zero: latitude in degrees
    Note:
        Equation is an approximation within `lat_zero +/- 0.5` degree.
    '''
    lat_zero = np.deg2rad(lat_zero)
    return 111412.84 * np.cos(lat_zero) - 93.5 * np.cos(3 * lat_zero) \
            + 0.118 * np.cos(5 * lat_zero)


def lat_long_to_x_y(latitude, longitude, lat_zero=0, long_zero=0):
    '''
    Convert geographical coords to XY plane.

    By default, reference is set in (lat=0, long=0) point on the geosphere. 
    Pass these values to center XY coords at Warsaw (52.232222, 21.008333)
    Returns:
        `(x, y)` point coords in meters on XY plane centered in 
        `(lat_zero, long_zero)`.
    '''
    x = (longitude - long_zero) * k_long(lat_zero)
    y = (latitude - lat_zero) * k_lat(lat_zero)
    return x, y


class GraphGenerator:
    def __init__(self, outposts, gmaps=False):
        graph_array = [] 

        self.ref_id = 0
        self.ref_lat = outposts.iloc[self.ref_id].latitude
        self.ref_long = outposts.iloc[self.ref_id].longitude
        for i, a in enumerate(outposts[['latitude', 'longitude']].values):
            for j, b in enumerate(outposts[['latitude', 'longitude']].values):
                if i==j:
                    continue
                distance = self.get_distance(a, b, gmaps)
                graph_array.append([i, j, distance])
        self.graph_df = pd.DataFrame(graph_array, columns=["node_a", "node_b", "cost"])


    def get_distance(self, position_a, position_b, gmaps=False):
        assert not gmaps, "Google Maps is not supported yet!"
        x, y = lat_long_to_x_y(position_a[0], position_a[1], position_b[0], position_b[1])
        return (x ** 2 + y ** 2) ** 0.5 # For larger distances it's not true

