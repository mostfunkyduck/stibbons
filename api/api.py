import datetime
import logging
import json
import flask
from requests import HTTPError
from flask import request
from lib import forecast, api, location, feed

app = flask.Flask(__name__)
ACCESS_LOGGER_NAME = 'stibbons_access_log'

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
    xml_feed = feed.generate_feed(raw_feed, loc)
    return api.build_response(
            status=200,
            message=xml_feed
            )

@app.after_request
def hacky_access_log(response):
    '''
    This is a way to do crude access logging without worrying about PasteDeploy like the docs recommend
    Idea lifted from 'https://stackoverflow.com/questions/52372187/logging-with-command-line-waitress-serve'
    '''
    timestamp = datetime.datetime.utcnow().strftime('[%Y-%b-%d %H:%M]')
    logger = logging.getLogger(ACCESS_LOGGER_NAME)
    logger.info('%s %s %s %s %s %s %s', timestamp, request.headers.get('X-Forwarded-For'), request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response
