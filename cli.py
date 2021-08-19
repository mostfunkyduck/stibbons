#!/usr/bin/env python3
import sys
import argparse
from lib import forecast, location, feed, db

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Scrape NOAA forecasts')
    parser.add_argument('--static-path', help='path to static file with NOAA HTML')
    parser.add_argument('--location', help='location to look up dynamically')
    return parser.parse_args()

def parse_static_path(path: str) -> str:
    lines = []
    with open(path) as fd:
        lines = fd.readlines()
    return ''.join(lines)

def main():
    args = parse_args()
    db.init()
    body = ''
    if args.static_path:
        print(f'parsing static file {args.static_path}', file=sys.stderr)
        body = parse_static_path(args.static_path)
        forecastDict = forecast.parse_forecast(body=body)
    elif args.location:
        print(f'looking up location {args.location}', file=sys.stderr)
        coordinates = location.lookup_coordinates(args.location)
        url = f'https://forecast.weather.gov/MapClick.php?lat={coordinates["latitude"]}&lon={coordinates["longitude"]}' 
        forecastDict = forecast.parse_forecast(url=url)
    else:
        print('must specify location or static path', file=sys.stderr)
        return
    print(feed.generate_feed(forecastDict, args.location or 'static'))

if __name__ == '__main__':
    main()
