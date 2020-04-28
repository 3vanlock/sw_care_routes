from secrets import GMAPS_API_KEY
from config import DEFAULT_START_ADDRESS

import argparse
import csv
import googlemaps
import jmespath
import logging as _log
import math

from datetime import date, timedelta
from os import path

def get_shortest(matrix):
    """Return the name of the address with the shortest drive time"""
    elements = jmespath.search('rows[].elements[]', matrix)
    shortest_time = min(jmespath.search('rows[].elements[].duration.value', matrix))
    # Loop through all elements to find index of shortest travel time, use to get address
    for i in range(len(elements)):
        if int(elements[i]['duration']['value']) == shortest_time:
            shortest_address = matrix['destination_addresses'][i]
    return shortest_address

def assemble_address(destination):
    return (f"{destination['address']['house_number']} {destination['address']['street']}, "
            f"{destination['address']['city']}, {destination['address']['state']} {destination['address']['zip']}, {destination['address']['country']}"
        )       

def create_route(client, origin, destinations):
    """Create route preferring shortest drive time between destinations"""
    route = list()
    route.append(origin)
    addresses = set()
    for destination in destinations:
        address = assemble_address(destination)
        addresses.add(address)
    while len(addresses) > 0:
        # Get travel time from most recent stop to remaining destinations
        matrix = client.distance_matrix(route[-1], addresses)
        # Find the address with the shortest travel time
        shortest_address = get_shortest(matrix)
        # Add that address to the route
        route.append(shortest_address)
        # Remove the address from remaining destinations
        try:
            addresses.remove(shortest_address)
        except KeyError:
            _log.error(f"Unable to match {addresses} with Google's name")
            _log.error(f"Run again using {shortest_address}")
            exit(1)
    return route


def load_destinations(file_path):
    destinations = list()
    if path.isfile(file_path):
        with open(file_path, 'r') as f:
            csvreader = csv.reader(f)
            for row in csvreader:
                destination = dict()
                destination['address'] = dict()
                destination['address']['house_number'] = row[0]
                destination['address']['street'] = row[1]
                destination['address']['city'] = row[2]
                destination['address']['zip'] = row[3]
                destination['address']['state'] = 'MI'
                destination['address']['country'] = 'USA'
                destination['contact'] = dict()
                destination['contact']['name'] = row[4]
                destination['contact']['phone'] = row[5]
                destinations.append(destination)
        return destinations
    else:
        _log.error(f"Unable to open destinations file at {file_path}")

def format_email(routes):
    delivery_date = date.today() + timedelta(days=1)
    for route in routes:
        message = ("Good morning!\n\n"

            "Thank you so much for volunteering to deliver food boxes! " 
            f"Your route for {delivery_date.strftime('%A, %B %d, %Y')} is below. " 
            "Boxes will be ready to pick up after 12:30pm and should be picked up before 4:30pm.\n\n"

            "Pick Up:\n"
            f"{route[0]}\n\n"

            "PICKUP PICTURES\n\n"

            "Delivery Route: \n"
        )
        for destination in route[1:]:
            message += f"{destination}\n"
        message += "\nGOOGLE MAPS LINK\n\n"
        message += "I've also attached a PDF with step by step directions. Please reply with any questions. Thanks again for your assistance\n\n"
        message += "Regards,\nEvan Lock"
        print(message)
        print("\n\n\n")

def main():
    _log.basicConfig(format='%(asctime)s | %(levelname)s | %(message)s ')

    _parser = argparse.ArgumentParser()
    _parser.add_argument(
        'drivers',
        help='Number of drivers to create routes for',
        type=int
    )
    _parser.add_argument(
        '--destinations-file',
        dest='destfile',
        help='File path of CSV file containing addresses and contact info', 
        default='./destinations.csv'
    )
    _parser.add_argument(
        '--origin', 
        default=DEFAULT_START_ADDRESS
    )
    _args = _parser.parse_args()
    gmc = googlemaps.Client(key=GMAPS_API_KEY)
    destinations = sorted(load_destinations(_args.destfile), key = lambda i: i['address']['zip'])
    routes = list()
    start = 0
    for i in range(1, _args.drivers + 1):
        route = list()
        end = math.floor(len(destinations) / _args.drivers) * i
        if i == _args.drivers:
            route = create_route(gmc, _args.origin, destinations[start:])
        else:
            route = create_route(gmc, _args.origin, destinations[start:end])
        routes.append(route)
        start = end
    format_email(routes)

if __name__ == '__main__':
    main()