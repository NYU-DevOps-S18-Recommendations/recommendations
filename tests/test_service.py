import unittest
import json
import logging
from flask_api import status    # HTTP Status Codes

import service

######################################################################
#  T E S T   C A S E S
######################################################################

# Product_id
PS4 = 1
PS3 = 31
CONTROLLER = 2


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
        service.Recommendation(0, product_id=PS4, recommended_product_id=CONTROLLER, recommendation_type="accessory").save()
        service.Recommendation(0, product_id=PS3, recommended_product_id=CONTROLLER, recommendation_type="accessory").save()
        self.app = service.app.test_client()

    def tearDown(self):
        service.Recommendation.remove_all()

    def test_get_recommendation(self):
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

    def test_get_recommendation_list(self):
        """ Get a list of Recommendations """
        resp = self.app.get('/recommendations')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
