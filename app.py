from secrets import GMAPS_API_KEY
from config import DEFAULT_START_HOUSE_NUMBER, DEFAULT_START_STREET, DEFAULT_START_CITY, DEFAULT_START_ZIP

import argparse
import csv
import googlemaps
import jmespath
import logging as _log
import math

from datetime import date, timedelta
from os import path

class Destination:
    def __init__(self, house_number, street, city, zip_code, name=None, phone=None):
        self.house_number = house_number
        self.street = street
        self.city = city
        self.zip = zip_code
        self.state = 'MI'
        self.country = 'USA'
        self.name = name
        self.phone = phone
        self.address = (f"{self.house_number} {self.street}, "
            f"{self.city}, {self.state} {self.zip}, "
            f"{self.country}"
        )   

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
    addresses = set()
    for destination in destinations:
        addresses.add(destination.address)
    while len(addresses) > 0:
        # Get travel time from most recent stop to remaining destinations
        matrix = client.distance_matrix(route[-1].address, addresses)
        # Find the address with the shortest travel time
        shortest_address = get_shortest(matrix)
        # Add that address to the route
        for destination in destinations:
            if shortest_address == destination.address:
                route.append(destination)
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
                destination = Destination(row[0], row[1], row[2], row[3], row[4], row[5])
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
            f"{route[0].address}\n\n"

            "PICKUP PICTURES\n\n"

            "Delivery Route: \n"
        )
        for destination in route[1:]:
            message += f"{destination.name} - {destination.phone}\n"
            message += f"{destination.address}\n\n"
        message += "GOOGLE MAPS LINK\n\n"
        message += "I've also attached a PDF with step by step directions. Please reply with any questions. Thanks again for your assistance\n\n"
        message += "Regards,\nEvan Lock"
        print(message)
        print("\n\n")

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

    _args = _parser.parse_args()
    gmc = googlemaps.Client(key=GMAPS_API_KEY)
    destinations = sorted(load_destinations(_args.destfile), key = lambda i: i.zip)
    origin = Destination(DEFAULT_START_HOUSE_NUMBER, DEFAULT_START_STREET, DEFAULT_START_CITY, DEFAULT_START_ZIP)
    routes = list()
    start = 0
    for i in range(1, _args.drivers + 1):
        route = list()
        end = math.floor(len(destinations) / _args.drivers) * i
        if i == _args.drivers:
            route = create_route(gmc, origin, destinations[start:])
        else:
            route = create_route(gmc, origin, destinations[start:end])
        routes.append(route)
        start = end
    format_email(routes)

if __name__ == '__main__':
    main()