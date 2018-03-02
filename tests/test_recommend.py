"""
Test cases for Recommend Model.

Test cases can be run with:
  nosetests
  coverage report -m

"""

import unittest
from models import Recommendation, DataValidationError


# Product_id
PS4 = 1
CONTROLLER = 2
ADAPTER = 3
PS5 = 11
MONSTER_HUNTER = 21
DISPLAY = 22
PS3 = 31


######################################################################
#  T E S T   C A S E S
######################################################################


class TestRecommendations(unittest.TestCase):
    """ Test Cases for Recommendations """

    def setUp(self):
        Recommendation.remove_all()

    def test_create_a_recommendation(self):
        """ Create a recommendation and assert that it exists """
        recommend_list = {'0': [CONTROLLER, ADAPTER], '1': [PS5], '2': [MONSTER_HUNTER, DISPLAY]}
        recommendation = Recommendation(product_id=PS4, recommend_list=recommend_list)

        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.id, 0)
        self.assertEqual(recommendation.product_id, PS4)
        self.assertEqual(recommendation.recommend_list['0'], [CONTROLLER, ADAPTER])
        self.assertEqual(recommendation.recommend_list['1'], [PS5])
        self.assertEqual(recommendation.recommend_list['2'], [MONSTER_HUNTER, DISPLAY])

    def test_add_a_recommendation(self):
        """ Create a recommendation and add it to the database """
        recommendations = Recommendation.all()
        self.assertEqual(recommendations, [])

        recommend_list = {'0': [CONTROLLER, ADAPTER], '1': [PS5], '2': [MONSTER_HUNTER, DISPLAY]}
        recommendation = Recommendation(product_id=PS4, recommend_list=recommend_list)

        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.product_id, PS4)
        recommendation.save()

        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(recommendation.id, 1)
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)

    def test_update_a_recommendation(self):
        """ Update a Recommendation """
        recommend_list = {'0': [CONTROLLER, ADAPTER], '1': [PS5], '2': [MONSTER_HUNTER, DISPLAY]}
        recommendation = Recommendation(product_id=PS4, recommend_list=recommend_list)
        recommendation.save()

        # Change it an save it
        recommendation.product_id = PS3
        recommendation.save()
        self.assertEqual(recommendation.id, 1)
        self.assertEqual(recommendation.product_id, PS3)

        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].product_id, PS3)

    def test_delete_a_recommendation(self):
        """ Delete a Recommendation """
        recommend_list = {'0': [CONTROLLER, ADAPTER], '1': [PS5], '2': [MONSTER_HUNTER, DISPLAY]}
        recommendation = Recommendation(product_id=PS4, recommend_list=recommend_list)
        recommendation.save()
        self.assertEqual(len(Recommendation.all()), 1)

        # delete the recommendation and make sure it isn't in the database
        recommendation.delete()
        self.assertEqual(len(Recommendation.all()), 0)

    def test_serialize_a_recommendation(self):
        """ Test serialization of a Recommendation """
        recommend_list = {'0': [CONTROLLER, ADAPTER], '1': [PS5], '2': [MONSTER_HUNTER, DISPLAY]}
        recommendation = Recommendation(product_id=PS4, recommend_list=recommend_list)
        data = recommendation.serialize()

        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], 0)
        self.assertIn('product_id', data)
        self.assertEqual(data['product_id'], PS4)
        self.assertIn('recommend_list', data)
        self.assertEqual(data['recommend_list'], recommend_list)

    def test_deserialize_a_recommendation(self):
        """ Test deserialization of a Recommendation """
        recommend_list = {'0': [CONTROLLER, ADAPTER], '1': [PS5], '2': [MONSTER_HUNTER, DISPLAY]}
        data = {'id': 1, 'product_id': PS4, 'recommend_list': recommend_list}
        recommendation = Recommendation()
        recommendation.deserialize(data)

        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.id, 1)
        self.assertEqual(recommendation.product_id, PS4)
        self.assertEqual(recommendation.recommend_list, recommend_list)

    def test_deserialize_with_no_product_id(self):
        """ Deserialize a Recommend without a name """
        recommendation = Recommendation()
        recommend_list = {'0': [CONTROLLER, ADAPTER], '1': [PS5], '2': [MONSTER_HUNTER, DISPLAY]}
        data = {"id": 0, 'recommend_list': recommend_list}
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_with_no_data(self):
        """ Deserialize a Pet with no data """
        pet = Recommendation()
        self.assertRaises(DataValidationError, pet.deserialize, None)

    def test_deserialize_wtih_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_find_recommendation(self):
        """ Find a Recommendation by product_id """
        Recommendation(product_id=PS3, recommend_list={'0': [], '1': [], '2': []}).save()
        recommend_list = {'0': [CONTROLLER, ADAPTER], '1': [PS5], '2': [MONSTER_HUNTER, DISPLAY]}
        ps4 = Recommendation(product_id=PS4, recommend_list=recommend_list)
        ps4.save()

        recommendation = Recommendation.find_by_product_id(ps4.product_id)
        self.assertIsNot(len(recommendation), 0)
        self.assertEqual(recommendation[0].id, ps4.id)
        self.assertEqual(recommendation[0].product_id, PS4)
        self.assertEqual(recommendation[0].recommend_list, recommend_list)

    def test_find_with_no_recommendation(self):
        """ Find a Recommend with no Recommends """
        recommendation = Recommendation.find(1)
        self.assertIs(recommendation, None)

    def test_recommend_not_found(self):
        """ Test for a Recommend that doesn't exist """
        Recommendation(0, PS4, {}).save()
        recommendation = Recommendation.find(2)
        self.assertIs(recommendation, None)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
