## Scheduled Tasks/Workers

### Beginning of Day Calculations (BOD Worker)
BOD worker runs every 30 minutes and grabs programs whose beginning of day is in the past 30 minutes and that are effective. 

What it does:
+ updates trade payment dates for offers that haven't been accepted yet (assumes that offer will be accepted today for setting trade payment date)
+ recalculates fees for pending offers
+ marks offers as invalid if they develop negative tenor days during recalculation
+ checks program status and places programs on hold if needed (sends notifications when this happens)

### End of Day Calculations (EOD Worker)
EOD worker also runs every 30 minutes and grabs programs who have had a close of business int he past 30 minutes and that are effective.

What it does:
+ liquidity pool updates: Captures daily snapshots of pool status including credit limits, utilization, and pending offers. Records insured portion of liquidity usage by policy.

+ Program performance tracking
  - calculates key metrics: traded amounts (from offers sold that day), outstanding balances, past due amounts, invoice values remaining
  - distributes performance metrics across syndicate funders based on their commitment percentages
  - updates program performance by syndicates

+ Program state management
  - closes inactive programs - programs with no outstanding balances

+ Date Assignment- updates program eod target dates

### Trading Window Worker
This worker loops over programs and identifies two problems and send notification as needed:
+ Past due invoices - when invoice.repayment_date is <= current date (in program TZ)

+ Credit over utilization - for this program, are there any sold offers where the funder has not sent money? If this offer would exceed the limit, (pool.credit_limit - pool.credit_used - program_offer_amount < 0), then notify funder

### Aggregate Invoice File Worker
This worker supports aggregate invoice file uploading by aggregating invoice files uploaded to an s3 bucket. 

Steps:
  + check for duplicate invoice references within the file and in the database - raise error if present
  + validates required fields present
  + validate file extension (must be csv)
  + sanitize html from inputs
  + create line item records (represent pre-aggregated invoices)
  + aggregates invoices
    - invoices are grouped by these 5 fields: [`supplier_id` `buyer_id` `currency` `invoice_date` `maturity_date`]
    - `description` and `unique_invoice_id` are set to nil 
    - it will be converted to an xlsx which will contain the aggregated invoices
    - each aggregated invoice will have a new invoice reference generated
