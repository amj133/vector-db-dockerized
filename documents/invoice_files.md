## Invoice Files
Below is an example invoice file:
| supplier_id | buyer_id | invoice_reference | net_invoice_amount | maturity_date | invoice_date | description | unique_invoice_id | credit_amount | gross_invoice_amount | currency |
|-------------|----------|-------------------|-------------------|---------------|--------------|-------------|-------------------|---------------|---------------------|----------|
| RBLUSD      | SRUUSD   | B12               | 10.00             | 9/30/25       | 8/12/25      |             |                   | 0             | 10.00               | USD      |
| RBLUSD      | SRUUSD   | B13               | 9.00              | 9/30/25       | 9/2/25       |             |                   | 0             | 9.00                | USD      |
| RBLUSD      | SRUUSD   | B14               | 8.00              | 9/30/25       | 9/2/25       |             |                   | 0             | 8.00                | USD      |

`supplier_id` is the supplier participant external id. `buyer_id` is the same. 
+ `gross_invoice_amount` - `credit_amount` = `net_invoice_amount`
Gross invoicea mount is like the "nominal" amount that actually appears on the invoice. The amount actually paid to the suppier by the funder is the `net_invoice_amount` * `advanced_rate`.

Invoice files can also have free field columns included. These free fields are specified on an organization level. The organization can specify the type (date, boolean, decimal, integer, string) and if the field is required or not.

### A note on dates
+ invoice date is the date the invoice was created/issued
+ trade date is when the offer in the system is accepted by the funder
+ trade payment date is when the funder sends money to the supplier for an offer
+ invoice maturity date is when the invoice matures and is due payment from the buyer
+ repayment date is the date when the supplier repays the funder for a given offer
