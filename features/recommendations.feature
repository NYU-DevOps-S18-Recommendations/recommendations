Feature: The store service back-end
  As a service provider
  I need a RESTful catalog service
  so that I can keep track of all the recommendations

Background:
  Given the following recommendations
      | id | product_id | recommended_product_id | recommendation_type | likes |
      |  1 | 31         |  2                     | accessory           | 1     |
      |  2 |  1         |  2                     | accessory           | 1     |
      |  3 | 11         | 21                     | cross-sell          | 1     |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendation RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Update a recommendation
  When I visit the "Home Page"
  And I set the "Id" to "3"
  And I press the "Retrieve" button
  Then I should see "11" in the "Product_ID" field
  When I change "Product_ID" to "12"
  And I press the "Update" button
  Then I should see the message "Success"
  When I set the "Id" to "3"
  And I press the "Retrieve" button
  Then I should see "12" in the "Product_ID" field
  # When I press the "Clear" button
  # And I press the "Search" button
  # Then I should see "12" in the results
  # Then I should not see "11" in the results
