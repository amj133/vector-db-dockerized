## Liquidity Pools
Liquidity pools are configured with a credit limit amount, a specific currency, a treatment, a type (either seller or obligor/buyer), a status (active, inactive, pending), and are either insured or not.

Treatment options specify how remaining credit is calculated. They include the following:
+ Include expected settlements: Credit limit - outstandings - pending offers + expected settlements
  - Expected settlements look at the trade payment date rule on the program (e.g. trade date plus 2 days) and overlaps with invoices expected to be paid in that timeframe (2 days) which are then added back to available credit
  - pending offers are those submitted by suppliers but not yet accepted
+ Available credit only: Credit limit - outstandings - pending offers
+ Include pending deposits: Credit limit - outstandings - pending offers + pending deposits (not yet approved)
