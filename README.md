# ecosim
An economy simulator

## Requirements
Create a python backend using flask that will allow to maintain a collection of accounting ledgers
The data will be stored to a sqlite, using some method that would allow for easy portability to other databases, i.e. Postgress or others

### Create the database structure
A separate utility allows to create the database sctructure on a blank database (sqllite to start with) 
The database has the following tables and fields
- agent_type: id, name, description
- agent: id, agent_type_id, name, description
- transaction_type: id, name, description, cr_account, dt_account, function
- ledger: id, agent_id
- ledger_account: id, name, type [profit_loss, balance_sheet, off_balance_sheet, fx_position]
- ledger_entries: id, datetime, currency, ledger_id, dt_ccy, dt_amount, cr_ccy, cr_amount, dt_account_id, cr_account_id 
- ledger_event: id, transaction_type_id, name, datetime, description, agent, agent2, ccy, ccy2, amount, amount2

### Create a module file: economy_events.py
Contains economy_event functions that are called when economy events happen
All functions have these parameters: description, agent, agent2, ccy, ccy2, amount, amount2
All functions generate one or more ledger_events that are written inmediately to the table ledger_event using the parameters received and the name of the function
Use the matching ledger_logic information for this function create the corresponding entries in the ledger_entries table

### Interface to the ledger_logic table
Store new ledger_logic records
Allows reading the ledger_logic for a given economic_event
Ledger event can be: payment, purchase, sale, borrow, payment, receipt, purchase_freezone, sale_freezone, purchase_import, sale_export,

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
- 8 name: unwanted, type: off_balance_sheet

### Basic transaction_types
Create the following transaction_types:
- 1 name: buy, cr_account: merchandises, dt_account: creditors
- 2 name: pay, dt_account: banks, cr_account: suppliers
- 3 name: sell, dt_account: clients, cr_account: sales
- 4 name: borrow, dt_account: bank, dt_account: creditors
- 5 name: lend, dt_account: debitors, cr_account: banks
- 6 name: receive, dt_account: debitors, cr_account: banks
- 7 name: interest_pay, dt_account: banks, cr_account: expenses
- 8 name: interest_receive, cr_account: banks, dt_account: income
- 9 name: unwanted_event, cr_account: unwanted, dt_account: expenses
- 10 name: wanted_event, dt_account: unwanted, cr_account: income


### Mirror transactions
Every time that an economic event happens of a given type and if two agents are involved, then the second agent will record a transaction in her ledger using the mirror logic. The mirror logic is as follows:
- purchase <-> sale
- borrow <-> lend
- pay <-> receive
- interest_pay <-> interest_receive
- unwanted_event <-> wanted_event


