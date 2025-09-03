## SCiCustomer Application Overview
SCiCustomer is a **Supply Chain Finance Web Application**.

This system connects four key participants:
- **Suppliers**: Companies that need financing for their invoices or accounts receivable.
- **Funders**: Financial institutions that finance offers submitted by suppliers. Offers are a group of invoices.
- **Buyers**: Companies that purchase goods/services from suppliers and owe money, or have accounts payable.

## Programs
Programs are the basic unit of the system. The participants in a program are a supplier, a buyer, a funder, and a service provider. Programs also have a particular currency, so one program cannot trade in multiple currencies. The service provider is primarily our company, PrimeRevenue, although in some few cases we allow white labeling, in which case an existing funder will then be the service provider. 

Programs may also have syndicated funder participants. In these cases there is a primary funder along with any number of syndicated funders who commit to a set percentage of the funding. For example, in `Program A`, `Funder B` may be the primary funder, `Funder C` may commit to 20% of funding, and `Funder D` may commit to 25% of funding`, leaving the primary funder, `Funder B` to commit to 100 - 20 - 25 = 55% of the funding.
