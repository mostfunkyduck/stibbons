from functools import wraps
from typing import Callable, Dict, Any, List
import json

import jsonschema
import flask
from lib import api

newsletter = {
    'type': 'object',
    'required': ['target_email', 'from_domain', 'title'],
    'properties': {
        'link': {
            'type': 'string',
            'description': 'a link to the newsletter\'s site',
        },
        'description': {
            'type': 'string',
            'description': 'description of the newsletter',
        },
        'title': {
            'type': 'string',
            'description': 'the user facing title of the newsletter',
        },
        'target_email': {
            'type': 'string',
            'format': 'email',
            'description': 'email address that the newsletter will be sent to'
        },
        'from_domain': {
            'type': 'string',
            'pattern': '\\S+.\\S+',
            'description': 'the domain that the newsletter will be sent from'
        }
    }
}

def validate_payload(payload_schema: Dict[Any, Any], methods: List[str]) -> Callable:
    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args: Any, **kw: Any) -> flask.Response:
            if flask.request.method in methods:
                if not flask.request.json:
                    return api.build_response(
                        status=400,
                        message=json.dumps({
                        'error': 'invalid json or content-type header'
                        })
                    )
                try:
                    jsonschema.validate(flask.request.json, payload_schema)
                except jsonschema.ValidationError as e:
                    return api.build_response(
                        status=400,
                        message = json.dumps({
                            'error': 'invalid schema in request',
                            'details': e.message
                        })
                    )
            return f(*args, **kw)
        return wrapper
    return decorator
