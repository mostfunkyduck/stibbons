import json
from typing import Dict, Any
from flask import Response
import flask
from lib import constants
headers = {
    'X-Clacks-Overhead': 'GNU Terry Pratchett',
    'Server': f'{constants.APP_NAME}/{constants.APP_VERSION}'
}

def build_response(message: str, status: int, mimetype: str='application/json') -> Response:
    return Response(
        response=message,
        status=status,
        mimetype=mimetype,
        headers=headers
    )

def bad_body() -> Response:
    return build_response(json.dumps({
            'error': 'invalid json or content-type header'
        }),
        status=400
    )

def get_json(request: flask.Request) -> Dict[str, Any]:
    return request.json or {}

def missing_key_in_body(key: str) -> Response:
    return build_response(
        message=json.dumps({
            'error': f'missing required key: "{key}"'
        }),
        status=400
    )
