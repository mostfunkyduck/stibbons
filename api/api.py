import datetime
import logging
import json
import re

import feedgenerator
import flask
from flask import request
from requests import HTTPError
from sendgrid.helpers.inbound.parse import Parse
from sendgrid.helpers.inbound.config import Config
from lib import forecast, api, location, feed, util, db, datatypes, schema

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
    from_domain  = re.sub(r'.*@', '', util.parse_email(payload['from']))
    if not target_email:
        return api.build_response(
            message=json.dumps({
                'error': '"to" is undefined'
            }),
            status=400
        )
    newsletter_configs = [each for each in db.get_newsletters(target_email, from_domain)]
    if not newsletter_configs:
        return api.build_response(
                status=403,
                message=f'message received, but discarded because no newsletter configuration was found to {target_email} from {from_domain}'
        )

    newsletter_config   = newsletter_configs[0]
    newsletter_feed     = newsletter_config['feed']
    if not newsletter_feed:
        return api.build_response(
                status=403,
                message=f'could not find feed for {newsletter_config["title"]} (from: {from_domain}, to: {target_email})'
            )
    db.save_feed_entry(datatypes.FeedEntry(
        publish_date    =   now,
        feed_id         =   newsletter_feed['feed_id'],
        contents        =   payload.get('html') or payload.get('Text') or 'email webhook contained no content',
        title           =   payload['subject'],
        unique_id       =   ''
    ))
    return api.build_response(
            status=200,
            message='entry saved'
    )

@app.route('/feeds/newsletter', methods=["GET"])
def get_newsletter_feed():
    feed_id = flask.request.args['feed']
    feed_config = db.get_feed(feed_id)

    new_feed = feedgenerator.Atom1Feed(
        title       =   feed_config['title'],
        link        =   feed_config['link'],
        description =   feed_config['description'],
        language='en',
    )

    for entry in db.get_feed_entries(feed_id):
        new_feed.add_item(
            title       =   entry['title'],
            pubdate     =   entry['publish_date'],
            unique_id   =   entry['unique_id'],
            link        =   '',
            description =   'Newsletter update',
            content     =   entry['contents'],
        )
    xml_feed = new_feed.writeString('utf-8')
    return api.build_response(
            status=200,
            message=xml_feed
            )

def add_newsletter() -> flask.Response:
    body = api.get_json(flask.request)

    target_email = body['target_email']
    from_domain = body['from_domain']

    newsletter_feed = datatypes.Feed(
        feed_id     =   '',
        title       =   body['title'],
        description =   body.get('description') or '',
        link        =   body.get('link') or ''
    )
    newsletter_config = datatypes.Newsletter(
        feed            =   newsletter_feed,
        target_email    =   target_email,
        from_domain     =   from_domain,
    )
    feed_id = db.add_newsletter_and_feed(newsletter_feed, newsletter_config)
    return api.build_response(
            message=json.dumps({
                'id': str(feed_id),
                'message': 'newsletter added'
            }),
            status=200
            )

def get_newsletters() -> flask.Response:
    target_email = request.args.get('target_email')
    from_domain  = request.args.get('from_domain')

    newsletter_configs = db.get_newsletters(target_email, from_domain)
    if not newsletter_configs:
        return api.build_response(
            message=json.dumps({
                'error': f'no newsletter to {target_email} from {from_domain} was found'
            }),
            status=404
        )

    return api.build_response(
        message=json.dumps({
            'newsletters': [each for each in newsletter_configs]
        }),
        status=200
    )

@app.route('/newsletters', methods=['POST', 'GET'])
@schema.validate_payload(schema.newsletter, methods=['POST'])
def newsletter() -> flask.Response:
    if flask.request.method == 'POST':
        return add_newsletter()
    elif flask.request.method == 'GET':
        return get_newsletters()
    return api.bad_body()

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
