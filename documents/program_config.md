## Programs
Programs are the basic unit of the system. The participants in a program are a supplier, a buyer, a funder, and a service provider. Programs also have a particular currency, so one program cannot trade in multiple currencies. The service provider is primarily our company, PrimeRevenue, although in some few cases we allow white labeling, in which case an existing funder will then be the service provider. 

Programs may also have syndicated funder participants. In these cases there is a primary funder along with any number of syndicated funders who commit to a set percentage of the funding. For example, in `Program A`, `Funder B` may be the primary funder, `Funder C` may commit to 20% of funding, and `Funder D` may commit to 25% of funding`, leaving the primary funder, `Funder B` to commit to 100 - 20 - 25 = 55% of the funding.

### Basic Program Configuration

+ Programs have a specificy currency such as `USD` or `EUR`.
+ Programs have an advanced rate, which is the percent of the invoice amount that the funder commits to funding. For example, if the advanced rate is 99% and the invoices in an offer total $100, the funder will send the supplier $99 on the trade payment date if they accept the offer.
+ Programs have a trading window, defined by the trading window open and trading window close times. Offers can only be accepted during this time.
+ Programs have a close of business (utilizes the same start time as trading window), which defines when settlements or reconciliations/deposits can be accepted for a particular day. After the close of business, an end of day worker will run to update program performance data and liquidity pool usage. More details on end of day worker below.
+ Programs have a time zone specified.
+ Program statuses include:
  - active: can trade
  - closed: essentially a soft delete for programs (still keep them in system)
  - inactive: Funders put the program in this status when they want it closed. The end of day worker will close any inactive programs that do not have any outstandings against them.
  - pending: have not been activated yet, either missing configuration data or program settings changed and not re-activated yet
  - on hold: programs are put on hold based on a program rule that specifies if invoices are past due. The rule allows for grace days to be specified (e.g. can be no more than 10 days overdue)
+ Programs can be set to be `Auto Accept`, more details below
+ Programs either have a processing type of `new` or `balance`. Balance programs will be explained in their own section.

### Program Fees
Program fees are charged per invoice, and are either payed to the service provider or the funder. The fees categories are:
+ funder margin
+ funder base rate
+ service provider
+ other

Fees are calculated per invoice and based on the number of days (tenor) from one of:
+ invoice date
+ trade date
+ trade payment date
+ invoice maturity date

to one of:
+ invoice date
+ trade date
+ trade payment date
+ invoice maturity date
+ repayment date

Typically a program will have a service provider fee, a funder base rate fee, and a funder interest fee configured.

If invoices uploaded by the supplier have negative tenor days according to the program fee configurations than they should be marked as invalid invoices.

### Program Calendars
Programs have two calendars set, a maturity calendar and a trade calendar. The trade calendar determines valid business days for offer acceptance and the maturity calendar determines valid business days for reconciliations.

### Program Bank Accounts
//////////TODO//////////

### Program Liquidity Pools
You can have an unlimited number of pools on a program. Generally it is 2 pools, 1 for seller and 1 for obligor/buyer. Each program has at least an overall pool that is across the entire seller group and defines the total amount that can be outstanding across all sellers at a given moment in time. Types on a pool are just used for reporting.

The effective credit limit on a program is the lower of the 2 credit limits assigned to the program, which is used to determining trade eligibility. For instance, if overall available credit is lower than the obligor pool on the program the overall pool will limit the capital available for the trade. 

If a program is insured it may have an overall liquidity pool covering those that are insured.  Set to the limit from the insurer. A pool may also be established for a specific child of an obligor/buyer.
