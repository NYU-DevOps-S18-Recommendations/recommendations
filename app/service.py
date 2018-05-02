"""Recommendation Service.

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
from app.models import Recommendation
from . import app
import logging
from flask import Flask, Response, jsonify, request, json, url_for, make_response
from flask_api import status
from flask_restplus import Api, Resource, fields
from models import Recommendation, DataValidationError

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

######################################################################
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Recommendations REST API Service',
          description='This is a Recommendations server.',
          doc='/apidocs/'
         )

# This namespace is the start of the path i.e., /recommendations
ns = api.namespace('recommendations', description='Recommendations operations')

# Define the model so that the docs reflect what can be sent
recommendations_model = api.model('Recommendations', {
    'id': fields.Integer(readOnly=True, description='The unique id assigned internally by service'),
    'product_id': fields.Integer(required=True, description='The product that recommendations is for'),
    'recommended_product_id': fields.Integer(required=True, description='The recommended products'),
    'recommendation_type': fields.String(required=True, description='The type of recommendation'),
    'likes': fields.Integer(readOnly=True, description='The number of likes for a recommendation')
})
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
    # return jsonify(name='Recommendations REST API Service',
    #                version='1.0',
    #                url=url_for('list_recommendations', _external=True)), HTTP_200_OK
    return app.send_static_file('index.html')

######################################################################
# LIST ALL & QUERY recommendations
######################################################################


@app.route('/recommendations', methods=['GET'])
def list_recommendations():
    """ Retrieves a list of recommendations from the database """
    results = []
    product_id = request.args.get('product_id')
    recommendation_type = request.args.get('recommendation_type')
    recommended_product_id = request.args.get('recommended_product_id')
    if product_id:
        message, return_code = query_recommendations_by_product_id(product_id)
    elif recommendation_type:
        message, return_code = query_recommendations_by_recommendation_type(recommendation_type)
    elif recommended_product_id:
        message, return_code = query_recommendations_by_recommended_product_id(recommended_product_id)
    else:
        results = Recommendation.all()
        message = [recommendation.serialize() for recommendation in results]
        return_code = HTTP_200_OK

    return jsonify(message), return_code

def query_recommendations_by_product_id(product_id):
    """ Query a recommendation from the database that have the same product_id """
    recommendations = Recommendation.find_by_product_id(int(product_id))
    if len(recommendations) > 0:
        message = [recommendation.serialize()
                   for recommendation in recommendations]
        return_code = HTTP_200_OK
    else:
        message = {'error': 'Recommendation with product_id: \
                    %s was not found' % str(product_id)}
        return_code = HTTP_404_NOT_FOUND

    return message, return_code

def query_recommendations_by_recommendation_type(recommendation_type):
    """ Query a recommendation from the database that have the same recommendation type """
    recommendations = Recommendation.find_by_recommend_type(str(recommendation_type))
    if len(recommendations) > 0:
        message = [recommendation.serialize()
                   for recommendation in recommendations]
        return_code = HTTP_200_OK
    else:
        message = {'error': 'Recommendation with product_id: \
                    %s was not found' % str(recommendation_type)}
        return_code = HTTP_404_NOT_FOUND

    return message, return_code

def query_recommendations_by_recommended_product_id(recommended_product_id):
    """ Query a recommendation from the database that have the same recommended product id """
    recommendations = Recommendation.find_by_recommend_product_id(int(recommended_product_id))
    if len(recommendations) > 0:
        message = [recommendation.serialize()
                   for recommendation in recommendations]
        return_code = HTTP_200_OK
    else:
        message = {'error': 'Recommendation with product_id: \
                    %s was not found' % str(recommended_product_id)}
        return_code = HTTP_404_NOT_FOUND

    return message, return_code

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
# Action: Increase the number of Likes
######################################################################


@app.route('/recommendations/<int:id>/likes', methods=['PUT'])
def like_recommendation(id):
    """ Increase the number of likes for a recommendation with matching id """
    recommendation = Recommendation.find(id)
    if not recommendation:
        message = {'error': 'Recommendation with product_id: %s was not found' % str(id)}
        return_code = HTTP_404_NOT_FOUND
    else:
        recommendation.likes += 1
        recommendation.save()
        message = recommendation.serialize()
        return_code = HTTP_200_OK

    return jsonify(message), return_code

######################################################################
# DELETE ALL RECOMMENDATIONS DATA (for testing only)
######################################################################

@app.route('/recommendations/reset', methods=['DELETE'])
def recommendations_reset():
    """ Removes all recommendations from the database """
    Recommendation.remove_all()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
#   U T I L I T Y   F U N C T I O N S
######################################################################


@app.before_first_request
def init_db(redis=None):
    """ Initlaize the model """
    Recommendation.init_db(redis)


def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print "Setting up logging..."
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
