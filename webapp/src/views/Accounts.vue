<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Chart of Accounts</h1>
    </div>
    <div class="d-flex justify-content-between mb-4">
      <button @click="toggleCreateAccountModal" class="btn btn-primary">Create New Account</button>
      <div class="search-box">
        <input type="text" v-model="searchTerm" placeholder="Search accounts..." class="form-control" />
      </div>
    </div>
    
    <!-- Using ModalForm component instead of custom modal -->
    <ModalForm
      :show="showCreateAccountModal"
      title="Create New Account"
      confirmText="Create Account"
      @confirm="createAccount"
      @cancel="toggleCreateAccountModal"
    >
      <form @submit.prevent="createAccount">
        <div class="form-group">
          <label for="accountNumber" class="form-label">Account Number:</label>
          <input type="text" id="accountNumber" v-model="newAccount.number" required class="form-control" />
        </div>
        
        <div class="form-group">
          <label for="accountName" class="form-label">Account Name:</label>
          <input type="text" id="accountName" v-model="newAccount.name" required class="form-control" />
        </div>
        
        <div class="form-group">
          <label for="accountType" class="form-label">Account Type:</label>
          <select id="accountType" v-model="newAccount.type" required class="form-control">
            <option value="asset">Asset</option>
            <option value="liability">Liability</option>
            <option value="income">Income</option>
            <option value="expense">Expense</option>
            <option value="equity">Equity</option>
          </select>
        </div>
      </form>
    </ModalForm>
    
    <LoadingIndicator v-if="loading" message="Loading accounts..." />
    
    <ErrorMessage
      v-else-if="error"
      :message="error"
      :retry="true"
      @retry="fetchAccounts"
    />
    
    <div v-else class="table-wrapper">
      <BaseTable
        :columns="columns"
        :items="filteredAccounts"
        :hasActions="true"
      >
        <template #actions="{ item }">
          <button @click="viewAccountDetails(item)" class="btn btn-primary btn-sm">View</button>
          <button @click="editAccount(item)" class="btn btn-warning btn-sm">Edit</button>
          <button @click="confirmDelete(item)" class="btn btn-secondary btn-sm">Delete</button>
        </template>
      </BaseTable>
    </div>
    
    <ConfirmDialog
      :show="showConfirmDialog"
      title="Confirm Delete"
      :message="confirmMessage"
      confirmText="Delete"
      :danger="true"
      @confirm="deleteAccount"
      @cancel="cancelDelete"
    />
  </div>
</template>

<script>
import { get, post, del } from '../services/apiService';
import { formatCurrency } from '../services/formatters';
import BaseTable from '../components/BaseTable.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';
import ErrorMessage from '../components/ErrorMessage.vue';
import ConfirmDialog from '../components/ConfirmDialog.vue';
import ModalForm from '../components/ModalForm.vue';

export default {
  name: 'AccountsView',
  components: {
    BaseTable,
    LoadingIndicator,
    ErrorMessage,
    ConfirmDialog,
    ModalForm
  },
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
      },
      showConfirmDialog: false,
      accountToDelete: null,
      confirmMessage: '',
      columns: [
        { key: 'number', label: 'Account Number' },
        { key: 'name', label: 'Name' },
        { key: 'type', label: 'Type' }
      ]
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
        this.showCreateAccountModal = false; // Close modal on success
        this.fetchAccounts();
      } catch (err) {
        console.error('Error creating account:', err);
        this.error = `Failed to create account: ${err.response?.data?.message || err.message}`;
      }
    },

    confirmDelete(account) {
      this.accountToDelete = account;
      this.confirmMessage = `Are you sure you want to delete account ${account.number} - ${account.name}?`;
      this.showConfirmDialog = true;
    },
    
    cancelDelete() {
      this.showConfirmDialog = false;
      this.accountToDelete = null;
    },

    async deleteAccount() {
      try {
        await del(`api/ledger/accounts/${this.accountToDelete.id}`);
        this.fetchAccounts();
      } catch (err) {
        console.error('Error deleting account:', err);
        this.error = `Failed to delete account: ${err.response?.data?.message || err.message}`;
      } finally {
        this.showConfirmDialog = false;
        this.accountToDelete = null;
      }
    },

    formatCurrency,
    
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
/* Component-specific styling */
.search-box {
  width: 250px;
}
</style>