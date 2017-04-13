Feature: The pet store service back-end
    As a Pet Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my pets

Background:
    Given the following pets
        | id | name       | category | available |
        |  1 | fido       | dog      | True      |
        |  2 | kitty      | cat      | True      |
        |  3 | leo        | lion     | True      |

Scenario: The server is running
    When I visit the "home page"
    Then I should see "Pet Demo REST API Service"
    Then I should not see "404 Not Found"

Scenario: List all pets
    When I visit "pets"
    Then I should see "fido"
    And I should see "kitty"
    And I should see "leo"

Scenario: Update a pet
    When I retrieve "pets" with id "1"
    And I change "category" to "big dog"
    And I update "pets" with id "1"
    Then I should see "big dog"

Scenario: Delete a pet
    When I visit "pets"
    Then I should see "fido"
    And I should see "kitty"
    When I delete "pets" with id "2"
    And I visit "pets"
    Then I should see "fido"
    And I should not see "kitty"
