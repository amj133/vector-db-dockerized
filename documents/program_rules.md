## Program Rules

### Program Rules: Program Level
+ Change program status: change program status to on hold when repayment date is greater than or equal to specified number of business or calendary days past due and the total advanced value remaning is greater than or equal to a specified amount. This rule is evaluated by the beginning of day work (elaborated on below).

### Program Rules: Offer Level
+ Limit advanced offer amount: Valid offers must have an advanced offer amout between a specified min and max. The rule will be evaluated on sell or acceptance.
+ Limit the number of invoices on an offer: Valid offers must have between a specified min and max number of invoices. The rule will be evaluated on sell or acceptance.
+ Limit the number of invoice tenor days: Valid offers must contain tenor days with min calendar days of specified amount and max calendar days of specified amount. Tenor days defined from invoice date, trade date, or trade payment date to maturity date or repayment date. The rule will be evaluated on sell or acceptance.
+ Set trade payment date: set trade payment date as specified number of business days from the date of acceptance (trade date).
+ Discard invoices on offer: invoices associated with an offer will be discarded during offer decline or offer reversal.

### Program Rules: Invoice Level
+ Unique invoice reference: Invoices must have a unique invoice reference. Gross amount and original maturity date can also be specified individually or together. For example, if a user enables this rule with gross amount also selected, then invoices can have duplicated invoice references and still be valid but must have unique invoice reference and gross amount combinations to be valid. This rule will be evaluated on upload.
+ Allow invoices past maturity: Allow invoices a specified number of calendar or business days after invoice maturity date evaluated on upload.
+ Support unapplied credit memo: When selected, it will allow negative invoice amounts on upload. Also give the user to select optional or required. If required is selected then all credit memos must be selected for an offer to be made.
