import unittest
import json
import logging
from flask_api import status    # HTTP Status Codes

from models import Recommendation
import service

######################################################################
#  T E S T   C A S E S
######################################################################

# Product_id
PS4 = 1
CONTROLLER = 2
ADAPTER = 3
PS5 = 11
MONSTER_HUNTER = 21
DISPLAY = 22
PS3 = 31


class TestRecommendationservice(unittest.TestCase):
    """ Recommendation service Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        service.app.debug = False
        service.initialize_logging(logging.INFO)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        service.Recommendation.remove_all()
        self.app = service.app.test_client()

    def tearDown(self):
        service.Recommendation.remove_all()

    def test_get_recommendation(self):
        ps4 = Recommendation(id=0, product_id=PS4, recommended_product_id=CONTROLLER, recommendation_type="accessory")
        ps4.save()

        """ Read a single Recommendation """
        resp = self.app.get('/recommendations/1')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['product_id'], PS4)
        self.assertEqual(data['recommended_product_id'], CONTROLLER)
        self.assertEqual(data['recommendation_type'], "accessory")
        self.assertEqual(data['likes'], 0)

    def test_get_recommendation_not_found(self):
        """ Read a Recommendation thats not found """
        resp = self.app.get('/recommendations/11')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_recommendation_by_product_id(self):
        """ Query Recommendations by the product_id """
        Recommendation(id=0, product_id=PS4, recommended_product_id=CONTROLLER, recommendation_type="accessory").save()
        Recommendation(id=0, product_id=PS4, recommended_product_id=PS5, recommendation_type="up-sell").save()
        Recommendation(id=0, product_id=PS4, recommended_product_id=MONSTER_HUNTER, recommendation_type="cross-sell").save()
        Recommendation(id=0, product_id=PS5, recommended_product_id=MONSTER_HUNTER, recommendation_type="cross-sell").save()

        resp = self.app.get('/recommendations/find_by_product_id/' + str(PS4))

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['product_id'], PS4)

    def test_query_recommendation_by_product_id_fail(self):
        """ Query Recommendations by the product_id that don't exist """
        Recommendation(id=0, product_id=PS4, recommended_product_id=CONTROLLER, recommendation_type="accessory").save()
        Recommendation(id=0, product_id=PS4, recommended_product_id=PS5, recommendation_type="up-sell").save()

        resp = self.app.get('/recommendations/find_by_product_id/' + str(PS5))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
