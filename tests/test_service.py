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


    def test_delete_recommendation(self):
        service.Recommendation(0, 2, 4, "up-sell", 1).save()
        service.Recommendation(0, 2, 3, "accessory", 2).save()

        # save the current number of recommendation for later comparrison
        recommendation_count = self.get_recommendation_count()
        self.assertEqual(recommendation_count, 2)
        
        # delete a recommendation
        resp = self.app.delete('/recommendations/1', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_recommendation_count()
        self.assertEqual(new_count, recommendation_count - 1)

######################################################################
# Utility functions
######################################################################

    def get_recommendation_count(self):
        """ save the current number of recommendations """
        resp = self.app.get('/recommendations')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
