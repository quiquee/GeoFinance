<template>
  <div class="accounts">
    <h1>Chart of Accounts</h1>
    <div class="accounts-controls">
      <button @click="toggleCreateAccountModal" class="btn-primary">Create New Account</button>
      <div class="search-box">
        <input type="text" v-model="searchTerm" placeholder="Search accounts..." />
      </div>
    </div>
    
    <!-- Create Account Modal -->
    <div v-if="showCreateAccountModal" class="modal">
      <div class="modal-content">
        <h2>Create New Account</h2>
        <form @submit.prevent="createAccount">
          <div class="form-group">
            <label for="accountNumber">Account Number:</label>
            <input type="text" id="accountNumber" v-model="newAccount.number" required class="form-control" />
          </div>
          
          <div class="form-group">
            <label for="accountName">Account Name:</label>
            <input type="text" id="accountName" v-model="newAccount.name" required class="form-control" />
          </div>
          
          <div class="form-group">
            <label for="accountType">Account Type:</label>
            <select id="accountType" v-model="newAccount.type" required class="form-control">
              <option value="asset">Asset</option>
              <option value="liability">Liability</option>
              <option value="income">Income</option>
              <option value="expense">Expense</option>
              <option value="equity">Equity</option>
            </select>
          </div>
          
          <div class="button-container">
            <button type="submit" class="btn-primary">Create Account</button>
            <button type="button" @click="toggleCreateAccountModal" class="btn-secondary">Cancel</button>
          </div>
        </form>
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
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="account in filteredAccounts" :key="account.id">
            <td>{{ account.number }}</td>
            <td>{{ account.name }}</td>
            <td>{{ account.type }}</td>
            <td class="actions">
              <button @click="viewAccountDetails(account)" class="btn-small">View</button>
              <button @click="editAccount(account)" class="btn-small btn-edit">Edit</button>
              <button @click="deleteAccount(account)" class="btn-small btn-secondary">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { get, post, del } from '../services/apiService';

export default {
  name: 'AccountsView',
  data() {
    return {
      accounts: [],
      loading: true,
      error: null,
      searchTerm: '',
      showCreateAccountModal: false,
      newAccount: {
        name: '',
        number: '',
        type: 'asset'
      }
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
        const response = await get('api/ledger/accounts');
        this.accounts = response.data;
      } catch (err) {
        console.error('Error fetching accounts:', err);
        this.error = `Failed to load accounts: ${err.message}`;
      } finally {
        this.loading = false;
      }
    },

    toggleCreateAccountModal() {
      this.showCreateAccountModal = !this.showCreateAccountModal;
      if (!this.showCreateAccountModal) {
        // Reset the form data when closing modal
        this.newAccount = {
          name: '',
          number: '',
          type: 'asset'
        }; 
      }
    },

    async createAccount() {
      try {
        await post('api/ledger/accounts', this.newAccount);
        this.toggleCreateAccountModal();
        this.fetchAccounts();
      } catch (err) {
        console.error('Error creating account:', err);
        alert(`Failed to create account: ${err.response?.data?.message || err.message}`);
      }
    },

    async deleteAccount(account) {
      if(!confirm(`Are you sure you want to delete account ${account.number} - ${account.name}?`)) {
        return;
      }
      
      try {
        await del(`api/ledger/accounts/${account.id}`);
        this.fetchAccounts();
      } catch (err) {
        console.error('Error deleting account:', err);
        alert(`Failed to delete account: ${err.response?.data?.message || err.message}`);
      }
    },

    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value);
    },
    viewAccountDetails(account) {
      alert(`View details for account: ${account.name}`);
    },
    editAccount(account) {
      alert(`Edit account: ${account.name}`);
    }
  },
  mounted() {
    document.title = 'GeoFinance - Accounts';
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

.btn-secondary {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
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

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

.button-container {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>