"""
Models for recommendation micro service.

All of the models are stored in this module

Models
------
Recommendation - A recommendation used in the service

Attributes:
-----------

product_id (int) - the product id of this recommendation
recommended_product_id (int) - the product id of being recommended
recommendation_type (string) - the type of this recommendation, should be
                               ('up-sell', 'cross-sell', 'accessory')
likes (int) - the count of how many people like this recommendation

"""
import os
import json
import logging
import threading
import pickle
from redis import Redis
from redis.exceptions import ConnectionError
from cerberus import Validator

#######################################################################
# Recommendations Model for database
#   This class must be initialized with use_db(redis) before using
#   where redis is a value connection to a Redis database
#######################################################################

class DataValidationError(Exception):
    """ Used for a data validation errors when deserializing."""
    pass


class Recommendation(object):
    """
    Class that represents a Recommendation.

    This version uses an in-memory collection of recommendations for testing
    """
    logger = logging.getLogger(__name__)
    lock = threading.Lock()
    redis = None
    schema = {
        'id': {'type': 'integer'},
        'product_id': {'type': 'integer', 'required': True},
        'recommended_product_id': {'type': 'integer', 'required': True},
        'recommendation_type': {'type': 'string', 'required': True},
        'likes':{'type': 'integer'}
        }
    __validator = Validator(schema)

    # data = []
    index = 0

    def __init__(self, id=0, product_id=0, recommended_product_id=0,
                 recommendation_type="", likes=0):
        """ Initialize a Recommendation """
        self.id = id
        self.product_id = product_id
        self.recommended_product_id = recommended_product_id
        self.recommendation_type = recommendation_type
        self.likes = likes

    def __repr__(self):
        return '<Recommendation %r>' % (self.product_id)

    def save(self):
        """
        Saves a Recommendation to the data store
        """
        if self.product_id == None:
            raise DataValidationError('product_id is not set')
        if self.id == 0:
            self.id = Recommendation.__next_index()
        Recommendation.redis.set(self.id, pickle.dumps(self.serialize()))

    def delete(self):
        """ Removes a Recommendation from the data store """
        Recommendation.redis.delete(self.id)

    def serialize(self):
        """ Serializes a Recommendation into a dictionary """
        return {"id": self.id,
                "product_id": self.product_id,
                "recommended_product_id": self.recommended_product_id,
                "recommendation_type": self.recommendation_type,
                "likes": self.likes}

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the Recommendation data
        """
        if isinstance(data, dict) and Recommendation.__validator.validate(data):
            self.id = data['id']
            self.product_id = data['product_id']
            self.recommended_product_id = data['recommended_product_id']
            self.recommendation_type = data['recommendation_type']
            self.likes = data['likes']
        else:
            raise DataValidationError('Invalid recommendation data: ' + str(Recommendation.__validator.errors))
        return self

    @staticmethod
    def __next_index():
        """ Generates the next index in a continual sequence """
        return Recommendation.redis.incr('index')

    @staticmethod
    def all():
        """ Returns all of the Recommends in the database """
        results = []
        for key in Recommendation.redis.keys():
            if key != 'index':
                data = pickle.loads(Recommendation.redis.get(key))
                recommendation = Recommendation(data['id']).deserialize(data)
                results.append(recommendation)

        return results

    @staticmethod
    def remove_all():
        """ Removes all of the Recommendations from the database """
        Recommendation.redis.flushall()

    @staticmethod
    def find(Recommendation_id):
        """ Finds a Recommendation by it's ID """
        if Recommendation.redis.exists(Recommendation_id):
            data = pickle.loads(Recommendation.redis.get(Recommendation_id))
            recommendation = Recommendation(data['id']).deserialize(data)
            return recommendation
        return None

    @staticmethod
    def __find_by(attribute, value):
        """ Generic Query that finds a key with a specific value """
        Recommendation.logger.info('Processing %s query for %s', attribute, value)
        if isinstance(value, str):
            search_criteria = value.lower()
        else:
            serach_criteria = value
        results = []
        for key in Recommendation.redis.keys():
            if key != 'index':
                data = pickle.loads(Recommendation.redis.get(key))
                if isinstance(data[attribute], str):
                    test_value = data[attribute].lower()
                else:
                    test_value = data[attribute]
                if test_value == search_criteria:
                    results.append(Recommendation(data['id']).deserialize(data))
        return results

    @staticmethod
    def find_by_product_id(product_id):
        """ Returns Recommend with the given product_id
        Args:
            product_id (int): the product_id of the Recommend you want to match
        """
        return Recommendation.__find_by('product_id', product_id)

    @staticmethod
    def find_by_recommend_product_id(recommended_product_id):
        """ Returns Recommend with the given product_id
        Args:
            recommend_product_id (int): the recommend_product_id of the Recommend you want to match
        """
        return Recommendation.__find_by('recommended_product_id', recommended_product_id)

    @staticmethod
    def find_by_recommend_type(recommendation_type):
        """ Returns Recommend with given recommendation_type
        Args:
            recommend_type (int): the recommend type of the Recommend you want to match
        """
        return Recommendation.__find_by('recommendation_type', recommendation_type)

    @staticmethod
    def find_by_likes(likes):
        """ Returns Recommends that have more likes
        Args:
            likes (int): the number of likes that a Recommend should have at least
        """
        return Recommendation.__find_by('likes', likes)

#######################################################################
# REDIS DATABASE CONNECTION METHODS
#######################################################################

    @staticmethod
    def connect_to_redis(hostname, port, password):
        """ Connects to Redis and tests the connection """
        Recommendation.logger.info("Testing Connection to: %s:%s", hostname, port)
        Recommendation.redis = Redis(host = hostname, port = port, password = password)
        try:
            Recommendation.redis.ping()
        except ConnectionError:
            Recommendation.redis = None
        return Recommendation.redis

    @staticmethod
    def init_db(redis = None):
        """
        Initialized Redis database connection

        This method will work in the following conditions:
            1) In Bluemix with Redis bound through VCAP_SERVICES
            2) With Redis running on the local server as with Travis CI
            3) With Redis --link in a Docker container called 'redis'
            4) Passing in your own Redis connection object
        Exception:
        ----------
            redis.ConnetionError - if ping() test failes
        """
        if redis:
            Recommendation.logger.info("Using client connection...")
            Recommendation.redis = redis
            try:
                Recommendation.redis.ping()
                Recommendation.logger.info("Connection established")
            except ConnectionError:
                Recommendation.logger.error("Client Connection Error!")
                Recommendation.redis = None
                raise ConnectionError('Could not connect to the Redis Service')
            return
        # Get the credentials from the Bluemix environment
        if 'VCAP_SERVICES' in os.environ:
            Recommendation.logger.info("Using VCAP_SERVICES...")
            vcap_services = os.environ['VCAP_SERVICES']
            services = json.loads(vcap_services)
            creds = services['rediscloud'][0]['credentials']
            Recommendation.logger.info("Conecting to Redis on host %s port %s",
                            creds['hostname'], creds['port'])
            Recommendation.connect_to_redis(creds['hostname'], creds['port'], creds['password'])
        else:
            Recommendation.logger.info("VCAP_SERVICES not found, checking localhost for Redis")
            Recommendation.connect_to_redis('127.0.0.1', 6379, None)
            if not Recommendation.redis:
                Recommendation.logger.info("No Redis on localhost, looking for redis host")
                Recommendation.connect_to_redis('redis', 6379, None)
        if not Recommendation.redis:
            # if you end up here, redis instance is down.
            Recommendation.logger.fatal('*** FATAL ERROR: Could not connect to the Redis Service')
            raise ConnectionError('Could not connect to the Redis Service')
