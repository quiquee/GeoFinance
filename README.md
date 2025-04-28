# ecosim
An economy simulator

## Requirements
Create a python backend using flask that will allow to maintain a collection of accounting ledgers
The data will be stored to a sqlite
There is an API that allows to configure the system, modify records, add or delete

The database will store:
Regions, Sectors, Agent Types, Agents, Ledgers, Economic Events, Accounting Rules, Accounts and Transactions

## Main definitions

### Region
Regions are systems where economic events happen
There is a main region called "World" 
A region that is not World is always a sub-region of another one
For example: Asia is a sub-region of world, and China is a sub-region of Asia

### Sector
Sectors are like regions, where economic events may happen. 
There is a main sector, called "Economy" 
A sector that is not "Economy" is allways a sub-sector of another one
For example: Electronics is a sub-sector of Economy and Chip Manufacturer is a a sub-sector of Electronics

### Agent
Agents always belong to a single Sector and to a single Region
There is a special agent called "Chaos" that belongs to "Economy" sector and "World" region
Agents have a type

### EconomicAmount
EconomicAmount is a numerical representation of value

### Currency
Currencies are units of measurement for EconomicAmounts

### Wealth
Wealth is an EconomicAmount that represents the wealth of an agent

### Accounts
Accounts are structured records that allow to assign a state at a given point in time to a financial information item. 
Accounts are of three different types: balance sheet, profit and loss or off balance sheet
Accounts may describe a Right or an Obligation (Balance Sheet Accounts) or a Source or Destination (Profit and Loss accounts). 

### Ledger
Ledger is a collection of accounts that belong to an agent. It has a state at every point in time, which is the collection of all the balances for each of the accounts of that agent at that point in time

### Economic Events
Economic events are those events that may happen in a region or in a sector at a given point in time between two agents
Economic events have a probability of happening, a periodic frequency and a time decay specified in number of periods
Ecomomic events have as well an EconomicAmount, a date and a time, a region, a sector and two agents involved
For example:
1. Pompeya EarthQuake: EconomicAmount is be the amount of Wealth destroyed by the Earth Quake in the Pompeya region that happened a given date. Agents are Chaos on one side and habitants of Pompeya in the other and sector is Economy
1. Construction of Santiago Bernabeu: EconomicAmount is the value of the cost of building SantiagoBernabeu in the seventies. Region is Madrid, Sector is Football. Agents are a Construction Company and RealMadrid FC
1. Payment of Santiago Bernabeu Building at a rate of 20% anually: a derived Economic Event of the previous one, transfering annually for an amount of 20% from the RealMadrid FC to the Construction Company

### Accounting Rules
Accounting Rule is the logic that defines the frequency, the source account and the destination account
There might be one of more Accounting Rules linked to an economic event

### Transactions
Transactions are the economic representation of Economic Events. They are generated when the Economic Event happens and are created using the Accounting Rules linked to that Economic Event. The balance of the source account specified in the Accounting Rule is decreased by the EconomicAmount of the event and the balance of the destination account  is increased by the same amount 

### Frequency
A measure of time at which Economic Events happen
It can be: Once, Daily, Weekly, Monthly, Quaterly, Annually

## Starting Records in the System
### Basic agent_types
Create agent types
- 1 name: individual, description: a basic individual
- 2 name: shop, description: a retailer
- 3 name: bank, description: commercial bank
- 4 name: central_bank, description: a central bank
- 5 name: producer, description: a producer of goods and services
- 6 name: public, description: a public entity
- 7 name: realisedrisk, description: sometimes things happen

### Basic agents
Create the following agents and corresponding ledgers
- 1 name: Enrique, agent_type: individual, description: a smart consumer
- 2 name: Amazon, agent_type: shop, description: a big online retailer
- 3 name: AEAT, agent_type: public, description: agencia estatal de la administracion tributaria
- 4 name: ChinHuan, agent_type: producer, description: a chinese factory
- 5 name: HSBC , agent_type: bank, description: a global bank
- 6 name: TheAbyss, agent type: realisedrisk
- 7 name: Insurer, agent type: realisedrisk

### Basic ledger accounts
Create the following accounts 
- 1 name: merchandises, type: balance_sheet
- 2 name: banks, type: balance_sheet
- 3 name: creditors, type: balance_sheeet
- 4 name: debitors, type: balance_sheeet 
- 5 name: sales, type: profit_loss 
- 6 name: expenses, type: profit_loss 
- 7 name: income, type: profit_loss 

### Basic Economic Events
Create the following transaction_types:
- 1 name: purchase, cr_account: merchandises, dt_account: creditors
- 2 name: pay, dt_account: banks, cr_account: suppliers
- 3 name: sale, dt_account: clients, cr_account: sales
- 4 name: borrow, dt_account: bank, dt_account: creditors
- 5 name: lend, dt_account: debitors, cr_account: banks
- 6 name: receipt, dt_account: debitors, cr_account: banks
- 7 name: interest_pay, dt_account: banks, cr_account: expenses
- 8 name: interest_receive, cr_account: banks, dt_account: income




