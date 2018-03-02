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
import logging
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing."""
    pass


class Recommendation(db.Model):
    """
    Class that represents a Recommendation.

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    logger = logging.getLogger(__name__)
    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer)
    recommend_list = db.Column(db.PickleType())

    def __repr__(self):
        return '<Recommendation %r>' % (self.product_id)

    def save(self):
        """
        Saves a Recommendation to the data store
        """
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Removes a Recommendation from the data store """
        db.session.delete(self)
        db.session.commit()

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
    def init_db(app):
        """ Initializes the database session """
        Recommendation.logger.info('Initializing database')
        Recommendation.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @staticmethod
    def all():
        """ Returns all of the Recommendations in the database """
        Recommendation.logger.info('Processing all Recommendations')
        return Recommendation.query.all()

    @staticmethod
    def find(Recommendation_id):
        """ Finds a Recommendation by it's ID """
        Recommendation.logger.info('Processing lookup for id %s ...', Recommendation_id)
        return Recommendation.query.get(Recommendation_id)

    @staticmethod
    def find_or_404(Recommendation_id):
        """ Find a Recommendation by it's id """
        Recommendation.logger.info('Processing lookup or 404 for id %s ...', Recommendation_id)
        return Recommendation.query.get_or_404(Recommendation_id)

    @staticmethod
    def find_by_product_id(product_id):
        """ Returns Recommend with the given product_id
        Args:
            product_id (int): the product_id of the Recommend you want to match
        """
        Recommendation.logger.info('Processing product_id query for %s ...', product_id)
        return Recommendation.query.filter(Recommendation.product_id == product_id)
