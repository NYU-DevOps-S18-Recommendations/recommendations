"""
Models for recommendation micro service.

All of the models are stored in this module

Models
------
Recommendation - A recommendation used in the service

Attributes:
-----------
product_id (int) - the product id of this recommendation
recommend_list (dictionary) - a dictionary to get a list of product ids of
                              recommends, corresponding to the key as type
                              0: requires, 1: up-sell, 2: cross-sell

"""
import threading


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing."""
    pass


class Recommendation(object):
    """
    Class that represents a Recommendation.

    This version uses an in-memory collection of recommendations for testing
    """
    lock = threading.Lock()
    data = []
    index = 0

    def __init__(self, id=0, product_id=0, recommend_list={}):
        """ Initialize a Recommendation """
        self.id = id
        self.product_id = product_id
        self.recommend_list = recommend_list

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
                "recommend_list": self.recommend_list}

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the Recommendation data
        """
        try:
            self.id = data['id']
            self.product_id = data['product_id']
            self.recommend_list = data['recommend_list']
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
        recommends = [recommend for recommend in Recommendation.data if recommend.id == Recommendation_id]
        if recommends:
            return recommends[0]
        return None

    @staticmethod
    def find_by_product_id(product_id):
        """ Returns Recommend with the given product_id
        Args:
            product_id (int): the product_id of the Recommend you want to match
        """
        return [recommend for recommend in Recommendation.data if recommend.product_id == product_id]
