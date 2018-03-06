"""
Recommendation Service

This is an example of a recommendation service written with Python Flask
It demonstrates how a RESTful service should be implemented.

Paths
-----
GET  /recommendations - Retrieves a list of recommendations from the database
GET  /recommendations/{id} - Retrieves a recommendation with a specific id
POST /recommendations - Creates a recommendation in the datbase from the posted database
PUT  /recommendations/{id} - Updates a recommendation in the database fom the posted database with a specific id
DELETE /recommendations{id} - Removes a recommendation from the database that matches the id
"""

import os
import sys
import logging
from flask import Flask, Response, jsonify, request, json, url_for, make_response
from models import Recommendation, DataValidationError

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

# Create Flask application
app = Flask(__name__)

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

######################################################################
# Error Handlers
######################################################################

@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles all data validation issues from the model """
    return bad_request(error)


@app.errorhandler(400)
def bad_request(error):
    """ Handles requests that have bad or malformed data """
    return jsonify(status=400, error='Bad Request', message=error.message), 400


@app.errorhandler(404)
def not_found(error):
    """ Handles recommendations that cannot be found """
    return jsonify(status=404, error='Not Found', message=error.message), 404


@app.errorhandler(405)
def method_not_supported(error):
    """ Handles bad method calls """
    return jsonify(status=405, error='Method not Allowed',
                   message='Your request method is not supported.' \
                   ' Check your HTTP method and try again.'), 405



@app.errorhandler(500)
def internal_server_error(error):
    """ Handles catostrophic errors """
    return jsonify(status=500, error='Internal Server Error', message=error.message), 500


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Return something useful by default """
    return jsonify(name='Recommendations REST API Service',
                   version='1.0',
                   url=url_for('list_recommendations', _external=True)), HTTP_200_OK

######################################################################
# LIST ALL recommendationS
######################################################################


@app.route('/recommendations', methods=['GET'])
def list_recommendations():
    """ Retrieves a list of recommendations from the database """
    results = []
    category = request.args.get('category')
    if category:
        results = Recommendation.find_by_category(category)
    else:
        results = Recommendation.all()

    return jsonify([recommendation.serialize() for recommendation in results]), HTTP_200_OK

######################################################################
# RETRIEVE A recommendation
######################################################################


@app.route('/recommendations/<int:id>', methods=['GET'])
def get_recommendations(id):
    """ Retrieves a recommendation with a specific id """
    recommendation = Recommendation.find(id)
    if recommendation:
        message = recommendation.serialize()
        return_code = HTTP_200_OK
    else:
        message = {'error' : 'Recommendation with id: %s was not found' % str(id)}
        return_code = HTTP_404_NOT_FOUND

    return jsonify(message), return_code

######################################################################
# ADD A NEW recommendation
######################################################################


@app.route('/recommendations', methods=['POST'])
def create_recommendations():
    """ Creates a recommendation in the database from the posted database """
    payload = request.get_json()
    recommendation = Recommendation()
    recommendation.deserialize(payload)
    recommendation.save()
    message = recommendation.serialize()
    response = make_response(jsonify(message), HTTP_201_CREATED)
    response.headers['Location'] = url_for('get_recommendations', id=recommendation.id, _external=True)
    return response

######################################################################
# UPDATE AN EXISTING RECOMMENDATION
######################################################################


@app.route('/recommendations/<int:id>', methods=['PUT'])
def update_recommendations(id):
    """ Updates a recommendation in the database fom the posted database """
    recommendation = Recommendation.find(id)
    if recommendation:
        payload = request.get_json()
        recommendation.deserialize(payload)
        recommendation.save()
        message = recommendation.serialize()
        return_code = HTTP_200_OK
    else:
        message = {'error' : 'Recommendation with id: %s was not found' % str(id)}
        return_code = HTTP_404_NOT_FOUND

    return jsonify(message), return_code

######################################################################
# DELETE A recommendation
######################################################################


@app.route('/recommendations/<int:id>', methods=['DELETE'])
def delete_recommendations(id):
    """ Removes a recommendation from the database that matches the id """
    recommendation = Recommendation.find(id)
    if recommendation:
        recommendation.delete()
    return make_response('', HTTP_204_NO_CONTENT)


######################################################################
#   U T I L I T Y   F U N C T I O N S
######################################################################
def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print 'Setting up logging...'
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    print "*********************************"
    print " RECOMMENDATIONS  SERVICE "
    print "*********************************"
    initialize_logging()
    # dummy data for testing

    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
