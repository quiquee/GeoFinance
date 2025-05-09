copilot# GeoFinance API Documentation

This document provides a comprehensive overview of all endpoints available in the GeoFinance backend API.

## Authentication Endpoints

| Method | Endpoint | Description | Request Body | Response | Auth Required |
|--------|----------|-------------|-------------|----------|---------------|
| POST | `/api/login` | User login | `{"username": string, "password": string}` | User info including id, username, name, and role | No |
| POST | `/api/logout` | User logout | None | Success message | No |

## Account Endpoints

| Method | Endpoint | Description | Request Body | Response | Auth Required |
|--------|----------|-------------|-------------|----------|---------------|
| GET | `/api/accounts` | Get all accounts | None | List of all accounts | Yes |
| GET | `/api/accounts/<account_id>` | Get specific account by ID | None | Account details | Yes |
| POST | `/api/accounts` | Create new account | `{"name": string, "number": string, "type": string}` | Created account data | Yes |
| PUT | `/api/accounts/<account_id>` | Update existing account | `{"name": string, "number": string, "type": string}` | Updated account data | Yes |
| DELETE | `/api/accounts/<account_id>` | Delete account | None | Success message | Yes |

**Note**: Account deletion is only possible if the account has no transactions.

## Ledger Endpoints

| Method | Endpoint | Description | Query Parameters | Response | Auth Required |
|--------|----------|-------------|-----------------|----------|---------------|
| GET | `/api/ledger` | Get or create user's ledger | None | User ID and active ledger confirmation | Yes |
| DELETE | `/api/ledger` | Delete user's ledger | None | Success message | Yes |
| GET | `/api/ledger/balance` | Get account balances | None (optional `start_date`, `end_date` in YYYY-MM-DD) | List of accounts with their current balances | Yes |
| GET | `/api/ledger/trial-balance` | Get trial balance report | `start_date` (optional, YYYY-MM-DD), `end_date` (optional, YYYY-MM-DD) | Trial balance data with totals and balance status | Yes |
| GET | `/api/ledger/income-statement` | Get income statement | None | Income accounts, expense accounts, and summary totals | Yes |
| GET | `/api/ledger/balance-sheet` | Get balance sheet | Optional `as_of_date` (YYYY-MM-DD) | Categorized accounts and summary totals as of the given date | Yes |
| GET | `/api/ledger/history` | Get 12-month income/expense history | None | Historical data of income and expenses | Yes |

**Note**: Ledger deletion is only possible if there are no journal entries.

## Journal Endpoints

| Method | Endpoint | Description | Request Body | Response | Auth Required |
|--------|----------|-------------|-------------|----------|---------------|
| GET | `/api/journal/entries` | Get all journal entries | None (optional `start_date`, `end_date` in YYYY-MM-DD) | List of journal entries sorted by date (descending) | Yes |
| GET | `/api/journal/entries/<entry_id>` | Get specific journal entry | None | Journal entry details | Yes |
| POST | `/api/journal/entries` | Create journal entry | `{"description": string, "lines": array}` | Created journal entry data | Yes |
| PUT | `/api/journal/entries/<entry_id>` | Update journal entry | `{"description": string, "lines": array}` | Updated journal entry data | Yes |
| DELETE | `/api/journal/entries/<entry_id>` | Delete journal entry | None | Success message | Yes |

**Note**: Journal entries require at least two transaction lines and total debits must equal total credits.

### Transaction Line Format

When creating or updating journal entries, each transaction line in the `lines` array should have the following structure:

```json
{
  "account_id": integer,
  "amount": string,
  "type": string  // "debit" or "credit"
}
```

## Authentication Requirements

Most endpoints require authentication through a session-based login system. To authenticate:

1. First call the `/api/login` endpoint with valid credentials
2. The server will set session cookies that must be included in subsequent requests
3. Requests without valid session cookies to endpoints requiring authentication will return a 401 error

## Data Types

- **AccountType**: Can be one of the following values:
  - ASSET
  - LIABILITY
  - INCOME
  - EXPENSE
  - OFF_BALANCE