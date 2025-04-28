# ecosim
An economy simulator

## Requirements
Create a python backend using flask that will allow to maintain a collection of accounting ledgers
The data will be stored to a sqlite
There is an API that allows to configure the system, modify records, add or delete

The database will store:
Regions, Sectors, Agent Types, Agents, Ledgers, Economic Events, Accounting Rules, Accounts and Transactions


## Missing Key Information
1. **API Endpoints**: The API specification (routes, methods, request/response formats) needs to be defined
2. **Database Schema**: Complete database schema with relationships, constraints, and fields is required
3. **Authentication/Authorization**: Security requirements for the API access are not defined
4. **Project Structure**: The organization of the code and components is not outlined

## Inconsistencies & Clarifications Needed
1. **Mirror Transaction Description**: The documentation states "The destination account of the first agent becomes the source account of the first agent" - this appears to be incorrect and should likely read "...source account of the second agent"

2. **Agent Roles**: The roles of agents in transactions (sender/receiver) need further clarification

3. **Economic Event Mechanics**: How probability, frequency and time decay interact needs explanation

4. **Account References**: The accounting rules reference accounts that aren't defined in the basic ledger accounts:
   - Rule #2 references "suppliers" which isn't defined
   - Rule #3 references "clients" which isn't defined

5. **Currency Exchange Rate**: The mechanism for updating and tracking exchange rates isn't specified

6. **Wealth Calculation**: More specific details on how wealth is calculated are needed

7. **Time Model**: There's no clear specification for how time advances in the simulation

8. **Event Triggering**: The mechanism for economic events triggering other events needs more detail

## Typos
1. "anually" should be "annually" 

## Main definitions

### Region
Regions are systems where economic events happen
There is a main region called "World" 
A region that is not World is always a sub-region of another one
For example: Asia is a sub-region of world, and China is a sub-region of Asia
Formal structure definition: (id, name, parent_region_id)

### Sector
Sectors are like regions, where economic events may happen. 
There is a main sector, called "Economy" 
A sector that is not "Economy" is always a sub-sector of another one
For example: Electronics is a sub-sector of Economy and Chip Manufacturer is a a sub-sector of Electronics
Formal structure definition: (id, name, parent_sector_id)

### Agent
Agents always belong to a single Sector and to a single Region
There is a special agent called "Chaos" that belongs to "Economy" sector and "World" region
Agents have only one Agent type


### EconomicAmount
EconomicAmount is a numerical representation of value
Data type specification: a FLOAT 

### Currency
Currencies are units of measurement for EconomicAmounts
There is a exchange rate between two given currencies at every point in time, which is the last rate available in the system

### Wealth
Wealth is an EconomicAmount that represents the wealth of an agent
Wealth at a given point in time is a calculated property of an agent that is calculated by adding up the balances in the agent's ledger at that point in time

### Accounts
Accounts are structured records that allow to assign a state at a given point in time to a financial information item. 
Accounts are of three different types: balance sheet, profit and loss or off balance sheet
Accounts may describe a Right or an Obligation (Balance Sheet Accounts) or a Source or Destination (Profit and Loss accounts). 
Formal structure definition: (id, name, description, type)
There are instances of accounts in each ledger, they are created automatically whenever a transaction involving that account is first created

### Ledger
Ledger is a collection of accounts that belong to an agent. It has a state at every point in time, which is the collection of all the balances for each of the accounts of that agent at that point in time
Each agent has only one ledger
Ledgers are empty until a transaction is created

### Economic Events
Economic events are those events that may happen in a region or in a sector at a given point in time between two agents
Economic events have a probability of happening, a periodic frequency and a time decay specified in number of periods
Economic event instances have as well an EconomicAmount, a date and a time, a region, a sector and two agents involved
For example:
1. Pompeya EarthQuake: EconomicAmount is be the amount of Wealth destroyed by the Earth Quake in the Pompeya region that happened a given date. Agents are Chaos on one side and habitants of Pompeya in the other and sector is Economy
1. Construction of Santiago Bernabeu: EconomicAmount is the value of the cost of building SantiagoBernabeu in the seventies. Region is Madrid, Sector is Football. Agents are a Construction Company and RealMadrid FC
1. Payment of Santiago Bernabeu Building at a rate of 20% annually: a derived Economic Event of the previous one, transfering annually for an amount of 20% from the RealMadrid FC to the Construction Company
Economic events have templates that are used to instantiate a new Economic Event when the event happens. All derived events of a new event happening are then be triggered randonly using the probability specified in the Economic Event template
The roles of the agent in the transaction are specified using accounting rules linked to the new economic event

### Accounting Rules
Accounting Rule is the logic that defines the source account and the destination account involved in an economic event
There might be one of more Accounting Rules linked to an economic event
An accounting rule has this structure: source_account, destination_account
Accounting rules are generic, this is, they are common to all ledgers

### Transactions
Transactions are the economic representation of Economic Events. They are generated when the Economic Event happens and are created using the Accounting Rules linked to that Economic Event. The balance of the source account specified in the Accounting Rule is decreased by the EconomicAmount of the event and the balance of the destination account is increased by the same amount 
If there are two agents in the Economic Event, then two transactions are created for each accounting rule, each of them in the ledger of the 2 involved agents. The second transaction created by an accounting rule is called a mirror transaction and it involves the accounts in the ledger of the second agent. The source_account of the first agent becomes the destination account of the second agent. The destination account of the first agent becomes the source account of the first agent.
Formal structure: id, event_id, agent, source_account, destination_account, currency, economic amount

### Frequency
A measure of time at which Economic Events happen
It can be: Once, Daily, Weekly, Monthly, Quarterly, Annually
At every moment the system should check if new events should be triggered in a simulation and create them if they dont exist.
For example if we run a simulation for day 2 there are EconomicEvents with daily frequency, they should be created

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
- 1 name: Enrique, agent type: individual, description: a smart consumer, region: Spain, Sector: Individuals
- 2 name: Amazon, agent type: shop, description: a big online retailer, region: Spain, Sector: Online Retail
- 3 name: AEAT, agent type: public, description: agencia estatal de la administracion tributaria, region: Spain, Sector: Public
- 4 name: ChinHuan, agent type: producer, description: a chinese factory, region: China, Sector: Electronics
- 5 name: HSBC , agent type: bank, description: a global bank, region: Spain, Sector: Financial
- 6 name: TheAbyss, agent type: realisedrisk, region: World, Sector: Economy
- 7 name: Insurer, agent type: realisedrisk, region: World, Sector: Economy

### Basic ledger accounts
Create the following account templates 
- 1 name: merchandises, type: balance_sheet
- 2 name: banks, type: balance_sheet
- 3 name: creditors, type: balance_sheet
- 4 name: debitors, type: balance_sheet 
- 5 name: sales, type: profit_loss 
- 6 name: expenses, type: profit_loss 
- 7 name: income, type: profit_loss 

### Basic Economic Event templates
- 1 name: purchase, Frequency: One, time decay: 1 , probability: 100%
- 2 name: pay, Frequency: One, time decay: 1 , probability: 100%
- 3 name: sale, Frequency: One, time decay: 1 , probability: 100%
- 4 name: borrow, Frequency: One, time decay: 1 , probability: 100%
- 5 name: lend, Frequency: One, time decay: 1 , probability: 100%
- 6 name: receipt, Frequency: One, time decay: 1 , probability: 100%
- 7 name: interest_pay, Frequency: One, time decay: 1 , probability: 100%
- 8 name: interest_receive, Frequency: One, time decay: 1 , probability: 100%

### Basic Accounting Rules
Create the following Accounting rules linked to corresponding economic events:
- 1 event: purchase, destination account: merchandises, source account: creditors
- 2 event: pay, source account: banks, destination account: suppliers
- 3 event: sale, destination account: clients, source account: sales
- 4 event: borrow, destination account: bank, source account: creditors
- 5 event: lend, destination account: debitors, source account: banks
- 6 event: receipt, destination account: debitors, source account: banks
- 7 event: interest_pay, source account: banks, destination account: expenses
- 8 event: interest_receive, destination account: banks, source account: income




