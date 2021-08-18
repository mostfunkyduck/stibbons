from flask import Response
from lib import constants
def build_response(message: str, status: int) -> Response:
    return Response(
        response=message,
        status=status,
        mimetype='application/json',
        headers={
            'X-Clacks-Overhead': 'GNU Terry Pratchett',
            'Server': f'{constants.APP_NAME}/{constants.APP_VERSION}'
        }
    )
