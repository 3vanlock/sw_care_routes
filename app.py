from secrets import GMAPS_API_KEY
from config import DEFAULT_START_ADDRESS

import argparse
import googlemaps
import jmespath

def get_shortest(matrix):
    """Return the name of the address with the shortest drive time"""
    elements = jmespath.search('rows[].elements[]', matrix)
    shortest_time = min(jmespath.search('rows[].elements[].duration.value', matrix))
    # Loop through all elements to find index of shortest travel time, use to get address
    for i in range(len(elements)):
        if int(elements[i]['duration']['value']) == shortest_time:
            shortest_address = matrix['destination_addresses'][i]
    return shortest_address

def create_route(client, origin, destinations):
    """Create route preferring shortest drive time between destinations"""
    route = list()
    route.append(origin)
    while len(destinations) > 0:
        # Get travel time from most recent stop to remaining destinations
        matrix = client.distance_matrix(route[-1], destinations)
        # Find the address with the shortest travel time
        shortest_address = get_shortest(matrix)
        # Add that address to the route
        route.append(shortest_address)
        # Remove the address from remaining destinations
        destinations.remove(shortest_address)
    print(route)

def main():
    _parser = argparse.ArgumentParser()
    _parser.add_argument('destinations', help='Pipe-separated list of destinations')
    _parser.add_argument('--origin', default=DEFAULT_START_ADDRESS)
    _args = _parser.parse_args()

    # Create a set for easy item removal
    destinations = set(_args.destinations.split('|'))
    gmc = googlemaps.Client(key=GMAPS_API_KEY)
    create_route(gmc, _args.origin, destinations)

if __name__ == '__main__':
    main()