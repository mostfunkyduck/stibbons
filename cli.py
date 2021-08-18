#!/usr/bin/env python3
import argparse
from lib import forecast

def parse_args() -> list:
    parser = argparse.ArgumentParser(description='Scrape NOAA forecasts')
    parser.add_argument('--static-path', help='for testing: path to static file with NOAA HTML')
    return parser.parse_args()

def parse_static_path(path: str) -> str:
    lines = []
    with open(path) as fd:
        lines = fd.readlines()
    return ''.join(lines)

def main():
    args = parse_args()

    body = ''
    if args.static_path:
        body = parse_static_path(args.static_path)

    print(forecast.parse_forecast(body=body))

if __name__ == '__main__':
    main()
