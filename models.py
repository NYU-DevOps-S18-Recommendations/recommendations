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
from redis import Redis
from redis.exceptions import ConnectionError


class DataValidationError(Exception):
    """ Used for a data validation errors when deserializing."""
    pass


class Recommendation(object):
    """
    Class that represents a Recommendation.

    This version uses an in-memory collection of recommendations for testing
    """
    lock = threading.Lock()
    data = []
    index = 0
    redis = None
    logger = logging.getLogger(__name__)

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
        if self.id == 0:
            self.id = self.__next_index()
            Recommendation.data.append(self)
        else:
            for i in range(len(Recommendation.data)):
                if Recommendation.data[i].id == self.id:
                    Recommendation.data[i] = self
                    break

    def delete(self):
        """ Removes a Recommendation from the data store """
        Recommendation.data.remove(self)

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
        try:
            self.id = data['id']
            self.product_id = data['product_id']
            self.recommended_product_id = data['recommended_product_id']
            self.recommendation_type = data['recommendation_type']
            self.likes = data['likes']
        except KeyError as error:
            raise DataValidationError('Invalid recommend: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid recommend: body of request contained' \
                                      'bad or no data')
        return self

    @staticmethod
    def __next_index():
        """ Generates the next index in a continual sequence """
        with Recommendation.lock:
            Recommendation.index += 1
        return Recommendation.index

    @staticmethod
    def all():
        """ Returns all of the Recommends in the database """
        return [recommend for recommend in Recommendation.data]

    @staticmethod
    def remove_all():
        """ Removes all of the Recommendations from the database """
        del Recommendation.data[:]
        Recommendation.index = 0
        return Recommendation.data

    @staticmethod
    def find(Recommendation_id):
        """ Finds a Recommendation by it's ID """
        if not Recommendation.data:
            return None
        recommends = [recommend for recommend in Recommendation.data
                      if recommend.id == Recommendation_id]
        if recommends:
            return recommends[0]
        return None

    @staticmethod
    def find_by_product_id(product_id):
        """ Returns Recommend with the given product_id
        Args:
            product_id (int): the product_id of the Recommend you want to match
        """
        return [recommend for recommend in Recommendation.data
                if recommend.product_id == product_id]

    @staticmethod
    def find_by_recommend_product_id(recommend_product_id):
        """ Returns Recommend with the given product_id
        Args:
            recommend_product_id (int): the recommend_product_id of the Recommend you want to match
        """
        return [recommend for recommend in Recommendation.data
                if recommend.recommended_product_id == recommend_product_id]

    @staticmethod
    def find_by_recommend_type(recommendation_type):
        """ Returns Recommend with given recommendation_type
        Args:
            recommend_type (int): the recommend type of the Recommend you want to match
        """
        return [recommend for recommend in Recommendation.data
                if recommend.recommendation_type == recommendation_type]

    @staticmethod
    def find_by_likes(likes):
        """ Returns Recommends that have more likes
        Args:
            likes (int): the number of likes that a Recommend should have at least
        """
        return [recommend for recommend in Recommendation.data
                if recommend.likes >= likes]

######################################################################
#  R E D I S   D A T A B A S E   C O N N E C T I O N   M E T H O D S
######################################################################

    @staticmethod
    def connect_to_redis(hostname, port, password):
        """ Connects to Redis and tests the connection """
        Recommendation.logger.info("Testing Connection to: %s:%s", hostname, port)
        Recommendation.redis = Redis(host=hostname, port=port, password=password)
        try:
            Recommendation.redis.ping()
            Recommendation.logger.info("Connection established")
        except ConnectionError:
            Recommendation.logger.info("Connection Error from: %s:%s", hostname, port)
            Recommendation.redis = None
        return Recommendation.redis

    @staticmethod
    def init_db(redis=None):
        """
        Initialized Redis database connection

        This method will work in the following conditions:
          1) In Bluemix with Redis bound through VCAP_SERVICES
          2) With Redis running on the local server as with Travis CI
          3) With Redis --link in a Docker container called 'redis'
          4) Passing in your own Redis connection object

        Exception:
        ----------
          redis.ConnectionError - if ping() test fails
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
