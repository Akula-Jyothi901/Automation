Feature: Automate FCC and SimPumps application interaction for PAP

  Background:
    Given the test environment for retalix product
    And the application connects to socket

  @PAP @Smoke
  Scenario Outline: Perform Basic PAP transaction
    Given Initializing GPI Interfaces
    When I select pump <pump_number>
    And Card Swiped on pump with <trackdata>
    And I Set the flow rate on pump to <flow_rate>
    And the nozzle is lifted on pump
    And the grade is selected on pump
    Then fueling is started on pump
    And fueling is stopped on pump
    And the socket connection is closed successfully

    Examples:
      | pump_number | trackdata                                | flow_rate |
      | "1"         | ";37144983511002=191210196051234500000?" | 50        |

  @PAP @Wip
  Scenario Outline: Cancel the PAP transaction(Keyboard configuration dependency)
    Given Initializing GPI Interfaces
    When I select pump <pump_number>
    And Card Swiped on pump with <trackdata>
    And I Set the flow rate on pump to <flow_rate>
    And the nozzle is lifted on pump
    And the grade is selected on pump
    And user attempts to cancel the transaction
    #Then the transaction should get cancelled

    Examples:
      | pump_number | trackdata                                | flow_rate |
      | "1"         | ";37144983511002=191210196051234500000?" | 50        |

  @PAP @Wip
  Scenario Outline: Cancelled Pay at Pump MSR Transaction with expired card(prompts dependency)
    Given Initializing GPI Interfaces
    When I select pump <pump_number>
    And a MSR swipe is performed with '<expired_card_data>' data
    Then the ICR should display the configured prompt 'Card expired'
    When I wait for the configured 'PROMPTTIMEOUT' time
    Then the ICR should display welcome prompt

  #Test: 7352
  @PAP @Smoke
  Scenario Outline: Perform PAP with Loyalty Manual Entry
    Given Initializing GPI Interfaces
    When I select pump <pump_number>
    And a MSR swipe is performed with <valid_loyalty_data> data
    And Card Swiped on pump with <trackdata>
    And I Set the flow rate on pump to <flow_rate>
    And the nozzle is lifted on pump
    And the grade is selected on pump
    Then fueling is started on pump
    And fueling is stopped on pump
    And I select the YES softkey for print receipt
    And the socket connection is closed successfully

    Examples:
      | pump_number | valid_loyalty_data           | trackdata                                | flow_rate |
      | "1"         | ";6277558500773916=0000000?" | ";37144983511002=191210196051234500000?" | 50        |

  @PAP @Wip
  Scenario Outline: Perform PAP with expired card
    Given Initializing GPI Interfaces
    When I select pump <pump_number>
    And the user swiped an expired credit card
    Then the PAP transaction is declined
    And the ICR should display welcome prompt
    And the socket connection is closed successfully

    Examples:
      | pump_number | trackdata                                |
      | "1"         | ";37144983511002=191210196051234500000?" |

  #Test: 7782
  @MemoryDump @Smoke
  Scenario Outline: Perform PAP and analyze the memory dump
    Given The user completes PAP transaction with pump <pump_number> and flow rate <flow_rate>
    When a dump file for <process_name> process is created from Task Manager
    Then check the dump file should not have any card info or sensitive info

    Examples:
      | pump_number | process_name | flow_rate |
      | "1"         | "RFS"        | "50"      |
      | "1"         | "PumpSrv"    | "50"      |

  @PAP @Smoke
  Scenario Outline: Perform Basic PAP Transaction Cancellation (after lifting the nozzle)
    Given Initializing GPI Interfaces
    When I select pump <pump_number>
    And the nozzle is lifted on pump
    And Card Swiped on pump with <trackdata>
    Then the transaction is cancelled using the softkey
    And the transaction volume and value are 0
    And the transaction status should be "Paid"
    And I hang up the nozzle
    And the socket connection is closed successfully

    Examples:
      | pump_number | trackdata                                | flow_rate |
      | "1"         | ";37144983511002=191210196051234500000?" | 50        |

  @PAP @Smoke
  Scenario Outline: Initiating Basic PAP Transaction and removing the transaction
    Given Initializing GPI Interfaces
    When I select pump <pump_number>
    And Card Swiped on pump with <trackdata>
    And I Set the flow rate on pump to <flow_rate>
    And the nozzle is lifted on pump
    And the grade is selected on pump
    Then fueling is started on pump
    And fueling is stopped on pump
    And I select the YES softkey for print receipt
    And I remove the pap transaction in Transaction control
    And verify the pumpsrv log for removed record
    And the socket connection is closed successfully

    Examples:
      | pump_number | trackdata                                | flow_rate |
      | "1"         | ";37144983511002=191210196051234500000?" | 50        |
