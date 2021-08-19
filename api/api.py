import json
import flask
from requests import HTTPError
from flask import request
from lib import forecast, api, location, feed

app = flask.Flask(__name__)

@app.route('/rss', methods=['GET'])
def get_forecast():
    loc = request.args.get('location')
    if not loc:
        return api.build_response(
                status=400,
                message=json.dumps({
                    'error': 'please specify a valid location'
                })
        )

    try:
        refreshInterval = int(request.args.get('refresh'))
        if not refreshInterval:
            refreshInterval = 24
    except (TypeError, ValueError):
        return api.build_response(
                status=400,
                message=json.dumps({
                    'error': '{request.args.get("refresh")} is not a valid refresh inteval'
                })
        )

    try:
        coordinates = location.lookup_coordinates(loc)
    except HTTPError as e:
        status = 400
        bad_status = None
        if e.response:
            bad_status = e.response.status_code
        message = f'error looking up coordinates for {loc}'
        if bad_status:
            message = f'{message}: got status code "{bad_status}"'

        return api.build_response(
            status=status,
            message=json.dumps({
                'error': message
            })
        )
    if not coordinates:
        return api.build_response(
            status=400,
            message=json.dumps({
                'error': f'{location} could not be converted to valid coordinates'
            })
        )
    raw_feed = forecast.parse_forecast(url=f'https://forecast.weather.gov/MapClick.php?lat={coordinates["latitude"]}&lon={coordinates["longitude"]}')
    xml_feed = feed.generate_feed(raw_feed, loc, refreshInterval)
    return api.build_response(
            status=200,
            message=xml_feed
            )
