"""
Error handlers

Handles all of the HTTP Error Codes as JSON
"""

from flask import jsonify, make_response
from app.server import app
from app.custom_exceptions import DataValidationError

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(400)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = error.message or str(error)
    app.logger.info(message)
    return make_response(jsonify(status=400, error='Bad Request', message=message), 400)

@app.errorhandler(404)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = error.message or str(error)
    app.logger.info(message)
    return make_response(jsonify(status=404, error='Not Found', message=message), 404)

@app.errorhandler(405)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = error.message or str(error)
    app.logger.info(message)
    return make_response(jsonify(status=405, error='Method not Allowed', message=message), 405)

@app.errorhandler(415)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = error.message or str(error)
    app.logger.info(message)
    return make_response(jsonify(status=415, error='Unsupported media type', message=message), 415)

@app.errorhandler(500)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = error.message or str(error)
    app.logger.info(message)
    return make_response(jsonify(status=500, error='Internal Server Error', message=message), 500)
