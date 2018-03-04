# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for the Recommendation Service

Test cases can be run with:
  nosetests
  coverage report -m
"""

import logging
import unittest
import json
from flask_api import status    # HTTP Status Codes
from models import Recommendation, DataValidationError
import service

######################################################################
#  T E S T   C A S E S
######################################################################
class TestRecommendationServer(unittest.TestCase):
    """ Pet Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        service.app.debug = False
        service.initialize_logging(logging.ERROR)

    def setUp(self):
        """ Runs before each test """
        service.Recommendation.remove_all()
        service.Recommendation(0, 2, 4, "up-sell", 1).save()
        service.Recommendation(0, 2, 3, "accessory", 2).save()
        self.app = service.app.test_client()

    def tearDown(self):
        """ Runs after each test """
        service.Recommendation.remove_all()


    def test_delete_recommendation(self):
        """ Delete a recommendation that exists """
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
        """ save the current number of pets """
        resp = self.app.get('/recommendations')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        # self.assertEqual(data[0]['product_id'], 2)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()