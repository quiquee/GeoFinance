<template>
  <div class="accounts">
    <h1>Chart of Accounts</h1>
    <div class="accounts-controls">
      <button @click="createNewAccount" class="btn-primary">Create New Account</button>
      <div class="search-box">
        <input type="text" v-model="searchTerm" placeholder="Search accounts..." />
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      <p>Loading accounts...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="fetchAccounts" class="btn-primary">Retry</button>
    </div>
    
    <div v-else class="accounts-container">
      <table class="accounts-table">
        <thead>
          <tr>
            <th>Account Number</th>
            <th>Name</th>
            <th>Type</th>
            <th>Balance</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="account in filteredAccounts" :key="account.id">
            <td>{{ account.number }}</td>
            <td>{{ account.name }}</td>
            <td>{{ account.type }}</td>
            <td>{{ formatCurrency(account.balance) }}</td>
            <td class="actions">
              <button @click="viewAccountDetails(account)" class="btn-small">View</button>
              <button @click="editAccount(account)" class="btn-small btn-edit">Edit</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { buildApiUrl, getHeaders } from '../config/api';
import { getAuthHeaders } from '../services/authService';

export default {
  name: 'AccountsView',
  data() {
    return {
      accounts: [],
      loading: true,
      error: null,
      searchTerm: ''
    }
  },
  computed: {
    filteredAccounts() {
      if (!this.searchTerm) return this.accounts;
      
      const term = this.searchTerm.toLowerCase();
      return this.accounts.filter(account => 
        account.name.toLowerCase().includes(term) || 
        account.number.toString().includes(term) ||
        account.type.toLowerCase().includes(term)
      );
    }
  },
  methods: {
    async fetchAccounts() {
      this.loading = true;
      this.error = null;
      
      try {
        console.log('Fetching accounts from:', buildApiUrl('api/ledger/accounts'));
        
        const response = await fetch(buildApiUrl('api/ledger/accounts'), {
          headers: getAuthHeaders()
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', Object.fromEntries([...response.headers.entries()]));
        
        // Check for empty response
        const text = await response.text();
        console.log('Raw response:', text);
        
        if (!text) {
          throw new Error('Empty response from server');
        }
        
        let data;
        try {
          // Try to parse as JSON
          data = JSON.parse(text);
        } catch (parseError) {
          console.error('Error parsing JSON:', parseError);
          throw new Error('Invalid JSON response from server');
        }
        
        if (!response.ok) {
          throw new Error(data.message || 'Failed to fetch accounts data');
        }
        
        // Make sure data is an array
        if (!Array.isArray(data)) {
          console.warn('Response is not an array, using empty array instead');
          this.accounts = [];
          return;
        }
        
        console.log('Parsed data:', data);
        this.accounts = data;
      } catch (err) {
        console.error('Error fetching accounts:', err);
        this.error = `Failed to load accounts: ${err.message}`;
      } finally {
        this.loading = false;
      }
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value);
    },
    createNewAccount() {
      // This function will be implemented later
      alert('Create account feature will be added soon');
    },
    viewAccountDetails(account) {
      // This function will be implemented later
      alert(`View details for account: ${account.name}`);
    },
    editAccount(account) {
      // This function will be implemented later
      alert(`Edit account: ${account.name}`);
    }
  },
  mounted() {
    document.title = 'GeoFinance - Chart of Accounts';
    this.fetchAccounts();
  }
}
</script>

<style scoped>
.accounts {
  padding: 20px;
}

.accounts-controls {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.search-box input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 250px;
}

.accounts-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.accounts-table th,
.accounts-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.accounts-table th {
  background-color: #f5f5f5;
}

.accounts-table tr:hover {
  background-color: #f9f9f9;
}

.btn-primary {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-small {
  padding: 5px 10px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
}

.btn-edit {
  background-color: #f0ad4e;
}

.loading, .error {
  text-align: center;
  padding: 30px;
}

.error {
  color: #dc3545;
}

.actions {
  white-space: nowrap;
}
</style>