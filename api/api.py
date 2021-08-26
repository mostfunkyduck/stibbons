import datetime
import logging
import json
import hashlib

import feedgenerator
import flask
from flask import request
from requests import HTTPError
from sendgrid.helpers.inbound.parse import Parse
from sendgrid.helpers.inbound.config import Config
from lib import forecast, api, location, feed, util, config, db, constants

sg_config = Config()

app = flask.Flask(__name__)
ACCESS_LOGGER_NAME = 'stibbons_access_log'

@app.route('/rss', methods=['GET'])
def rss():
    return get_forecast()

@app.route('/feeds/forecast', methods=['GET'])
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
            message=xml_feed,
            mimetype='application/atom+xml',
            )

@app.route('/webhook/sendgrid', methods=["POST"])
def sendgrid_webhook():
    now = datetime.datetime.utcnow()
    payload = Parse(sg_config, flask.request).key_values()
    if not payload:
        return api.build_response(
                status=400,
                message='no payload'
        )

    target_email = util.parse_email(payload['to'])
    if not target_email or target_email not in config.email_allowlist():
        return api.build_response(
                status=403,
                message=f'message accepted, but discarded because {target_email} is not an allowlisted email'
        )
    entry = {
        'publish_date': now,
        'target_email': target_email,
        'contents':     payload.get('html') or payload.get('Text') or 'email webhook contained no content',
        'title':        payload['subject'],
        'unique_id':    hashlib.md5(f'{target_email}{now.strftime("%Y%m%d%H%M%S")}{payload.get("email")}'.encode('utf-8')).hexdigest()
    }

    db.save_feed_entry(entry)
    return api.build_response(
            status=200,
            message='entry saved'
    )

@app.route('/feeds/newsletter', methods=["GET"])
def get_feed():
    target_email = request.args.get('target_email')
    if not target_email:
        return api.build_response(
                status=400,
                message=json.dumps({
                    'error': 'please specify a feed'
                })
        )

    if target_email not in config.email_allowlist():
        return api.build_response(
            status=404,
            message=json.dumps({
                'error': f'{target_email} is not a registered feed'
            })
        )
    new_feed = feedgenerator.Atom1Feed(
        title=f'Email newsletter feed from {target_email}',
        link='',
        description=f'Email newsletter from {target_email}, translated by {constants.APP_NAME}',
        language='en',
    )

    for entry in db.get_feed_entries(target_email=target_email):
        new_feed.add_item(
            title=f'{entry["title"]}',
            pubdate=entry['publish_date'],
            unique_id=entry['unique_id'],
            link='',
            description='Newsletter update',
            content=entry['contents'],
        )
    xml_feed = new_feed.writeString('utf-8')
    return api.build_response(
            status=200,
            message=xml_feed
            )

def add_newsletter() -> flask.Response:
    body = api.get_json(flask.request)
    if not body:
        return api.bad_body()

    # we need feed title, target email, from domain for better allowlisting
    feed_title = body.get('title')
    if not feed_title:
        return api.missing_key_in_body('title')

    target_email = body.get('target_email')
    if not target_email:
        return api.missing_key_in_body('target_email')

    from_domain = body.get('from_domain')

    db.add_newsletter(feed_title, target_email, from_domain)
    return api.build_response(message=json.dumps({'message': 'newsletter added'}), status=200)

def get_newsletter() -> flask.Response:
    target_email = request.args.get('target_email')
    if not target_email:
        return api.bad_body() #TODO update to better message

    newsletter_entry = db.get_newsletter(target_email)
    if not newsletter_entry:
        return api.build_response(
            message=json.dumps({
                'error': f'no newsletter named {target_email} was found'
            }),
            status=404
        )

    return api.build_response(
        message=json.dumps({
            'newsletter': newsletter_entry
        }),
        status=200
    )
@app.route('/newsletter', methods=['POST', 'GET'])
def newsletter() -> flask.Response:
    if flask.request.method == 'POST':
        return add_newsletter()
    elif flask.request.method == 'GET':
        return get_newsletter()
    return api.bad_body()

@app.route('/allowlist', methods=['POST', 'GET'])
def add_to_allowlist():
    if flask.request.method == 'POST':
        body = api.get_json(flask.request)
        if not body:
            return api.bad_body()

        if 'email' not in body:
            return api.build_response(
                status=400,
                message=json.dumps({
                    'error': 'no "email" property in body'
                })
            )
        email = body['email']
        db.add_to_allowlist(email)
        return api.build_response(
                status=200,
                message=json.dumps({
                    'email': email
                })
                )

    if flask.request.method == 'GET':
        allowlist = config.email_allowlist()
        return api.build_response(
            status=200,
            message=json.dumps({
               'allowlist': allowlist
            })
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
