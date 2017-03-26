######################################################################
# ERROR Handling
######################################################################

from flask import jsonify, make_response
from flask_api import status    # HTTP Status Codes
from server import app
from custom_exceptions import DataValidationError

@app.errorhandler(DataValidationError)
def request_validation_error(e):
    return make_response(jsonify(status=400, error='Bad Request', message=e.message), status.HTTP_400_BAD_REQUEST)

@app.errorhandler(404)
def not_found(e):
    return make_response(jsonify(status=404, error='Not Found', message=e.description), status.HTTP_404_NOT_FOUND)

@app.errorhandler(400)
def bad_request(e):
    return make_response(jsonify(status=400, error='Bad Request', message=e.message), status.HTTP_400_BAD_REQUEST)

@app.errorhandler(405)
def method_not_allowed(e):
    return make_response(jsonify(status=405, error='Method not Allowed', message='Your request method is not supported. Check your HTTP method and try again.'), status.HTTP_405_METHOD_NOT_ALLOWED)

@app.errorhandler(500)
def internal_error(e):
    return make_response(jsonify(status=500, error='Internal Server Error', message='Huston... we have a problem.'), status.HTTP_500_INTERNAL_SERVER_ERROR)
