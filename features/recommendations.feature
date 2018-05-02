Feature: The store service back-end
  As a service provider
  I need a RESTful catalog service
  so that I can keep track of all the recommendations

Background:
  Given the following recommendations
      | id | product_id | recommended_product_id | recommendation_type | likes |
      |  1 | 31         |  2                     | Accessory           | 1     |
      |  2 |  1         |  2                     | Accessory           | 1     |
      |  3 | 11         | 21                     | Cross-sell          | 1     |
      |  4 | 14         | 31                     | Up-sell             | 2     |

Scenario: The server is running
  When I visit the "Home Page"
  Then I should see "Recommendation RESTful Service" in the title
  And I should not see "404 Not Found"

Scenario: Create a recommendation
  When I visit the "Home Page"
  And I set the "Id" to "6"
  And I set the "Product_ID" to "21"
  And I set the "Recommended_Product_ID" to "51"
  And I choose the "Recommendation_Type" to be "Cross-sell"
  And I set the "Likes" to "0"
  And I press the "Create" button
  Then I should see the message "Success"

Scenario: Update a recommendation
  When I visit the "Home Page"
  And I set the "Id" to "3"
  And I press the "Retrieve" button
  Then I should see "11" in the "Product_ID" field
  Then I should see "21" in the "Recommended_Product_ID" field
  Then I should see "Cross-sell" in the "Recommendation_Type" field
  When I change "Product_ID" to "12"
  And I press the "Update" button
  Then I should see the message "Success"
  When I set the "Id" to "3"
  And I press the "Retrieve" button
  Then I should see "12" in the "Product_ID" field
  When I press the "Search" button
  Then I should see "12" in the results

Scenario: Delete a recommendation
    When I visit the "Home Page"
    And I press the "Search" button
    And I set the "Id" to "3"
    When I press the "Delete" button
    Then I should see the message "Recommendation successfully deleted!"

Scenario: Read a recommendation
    When I visit the "Home Page"
    And I set the "Id" to "2"
    When I press the "Retrieve" button
    Then I should see "1" in the "Product_ID" field
    Then I should see "2" in the "Recommended_Product_ID" field
    Then I should see "Accessory" in the "Recommendation_Type" field

Scenario: Like a recommendation
    When I visit the "Home Page"
    And I set the "Id" to "2"
    When I press the "Retrieve" button
    Then I should see "1" in the "Product_ID" field
    Then I should see "2" in the "Recommended_Product_ID" field
    Then I should see "Accessory" in the "Recommendation_Type" field
    Then I should see "1" in the "Likes" field
    When I press the "Like" button
    Then I should see "2" in the "Likes" field

Scenario: List all recommendations
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "31" in the results
    And I should see "1" in the results
    And I should see "11" in the results
    And I should see "14" in the results

Scenario: List all accessory recommendations
    When I visit the "Home Page"
    And I choose the "Recommendation_Type" to be "Accessory"
    And I press the "Search" button
    Then I should see "31" in the results
    And I should see "1" in the results
    And I should not see "11" in the results
    And I should not see "14" in the results

Scenario: Query a recommendation
  When I visit the "Home Page"
  And I set the "Product_ID" to "14"
  And I press the "Search" button
  Then I should see "4" in the results
  Then I should see "31" in the results
  Then I should see "Up-sell" in the results

Scenario: Like a recommendation
    When I visit the "Home Page"
    And I set the "Id" to "2"
    When I press the "Retrieve" button
    Then I should see "1" in the "Product_ID" field
    Then I should see "2" in the "Recommended_Product_ID" field
    Then I should see "Accessory" in the "Recommendation_Type" field
    Then I should see "1" in the "Likes" field
    When I press the "Like" button
    Then I should see "2" in the "Likes" field

Scenario: List all recommendations
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "31" in the results
    And I should see "1" in the results
    And I should see "11" in the results
    And I should see "14" in the results
