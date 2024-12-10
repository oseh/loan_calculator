## Checklist

### Setup & Guidelines
- [x] Use an in-memory store (no database needed).

### Loan Calculation Requirements
- [x] Input Parameters:
  - [x] Start Date (date)
  - [x] End Date (date)
  - [x] Loan Amount (numeric amount)
  - [x] Loan Currency (e.g., USD)
  - [x] Base Interest Rate (percentage)
  - [x] Margin (percentage)

  **Total Interest Rate = Base Interest Rate + Margin**

- [x] Use the simple interest formula:
  
  ```
  Simple Interest = P × r × n
  ```
  
  Where:
  - P = Principal (Loan Amount)
  - r = Interest rate (in decimal form, e.g., 5% = 0.05)
  - n = Term of loan in years (days/365)

### Output Requirements
- [x] For each day between Start and End Date:
  - [x] Daily Interest Amount without margin
  - [x] Daily Interest Amount including margin
  - [x] Accrual Date
  - [x] Number of Days elapsed since the Start Date
- [x] Total Interest for the entire period

### User Journey
- [x] User provides input parameters for a new loan calculation.
- [x] The system calculates and displays the daily interest breakdown and total interest.
- [x] The system stores the calculation in memory.
- [x] The user can view historic calculations.
- [x] The user can update an existing calculation with new parameters.

### extra 
- [x] caching lru for in memory data store.
- [x] help and auto completion.
- [x] compound interest.

### Todo 
- [] record change history for auditing.
- [] add adjustable breakdown periods.
- [] persist data in a database of some kind. 



