<template>
  <div class="journal">
    <h1>Journal Entries</h1>

    <div v-if="showCreateForm">
      <CreateJournalEntry
        :accounts="accounts"
        @success="handleCreateSuccess"
        @cancel="toggleCreateForm"
      />
    </div>

    <div v-else>
      <div class="journal-controls">
        <button @click="toggleCreateForm" class="btn-primary">Create New Journal Entry</button>
        <div class="filters">
          <input type="date" v-model="startDate" class="date-input" />
          <input type="date" v-model="endDate" class="date-input" />
          <button @click="applyDateFilter" class="btn-filter">Filter by Date</button>
        </div>
      </div>

      <div v-if="loading" class="loading">
        <p>Loading journal entries...</p>
      </div>

      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="fetchJournalEntries" class="btn-primary">Retry</button>
      </div>

      <div v-else>
        <div v-if="journalEntries.length === 0" class="no-entries">
          <p>No journal entries found.</p>
        </div>

        <div v-else class="journal-entries-list">
          <div class="journal-entries-header">
            <span class="col-id">Entry #</span>
            <span class="col-date">Date</span>
            <span class="col-desc">Description</span>
            <span class="col-total">Total Amount</span>
            <span class="col-actions">Actions</span>
          </div>
          
          <div 
            v-for="entry in journalEntries" 
            :key="entry.id" 
            class="journal-entry-row"
            @mouseover="hoveredEntry = entry.id"
            @mouseleave="hoveredEntry = null"
          >
            <span class="col-id">{{ entry.id }}</span>
            <span class="col-date">{{ formatDate(entry.date) }}</span>
            <span class="col-desc">{{ entry.description }}</span>
            <span class="col-total">{{ formatCurrency(calculateEntryTotal(entry)) }}</span>
            <span class="col-actions">
              <button @click="viewEntryDetails(entry)" class="btn-small">View</button>
              <button @click="editEntry(entry)" class="btn-small btn-edit">Edit</button>
              <button @click="deleteEntry(entry.id)" class="btn-small btn-delete">Delete</button>
            </span>
            
            <!-- Detailed view that appears on hover -->
            <div v-if="hoveredEntry === entry.id" class="entry-details-popup">
              <div class="popup-header">
                <h4>Entry #{{ entry.id }} - {{ formatDate(entry.date) }}</h4>
                <div>{{ entry.description }}</div>
              </div>
              
              <table class="entry-details-table">
                <thead>
                  <tr>
                    <th>Account</th>
                    <th>Debit</th>
                    <th>Credit</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(line, index) in processEntryLines(entry.lines)" :key="index">
                    <td>{{ line.account_name }}</td>
                    <td>{{ line.debit ? formatCurrency(line.debit) : '' }}</td>
                    <td>{{ line.credit ? formatCurrency(line.credit) : '' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CreateJournalEntry from './CreateJournalEntry.vue';
import { get, del } from '../services/apiService';

export default {
  name: 'JournalView',
  components: {
    CreateJournalEntry,
  },
  data() {
    return {
      journalEntries: [],
      loading: true,
      error: null,
      startDate: '',
      endDate: '',
      showCreateForm: false,
      accounts: [],
      hoveredEntry: null,
    };
  },
  methods: {
    async fetchAccounts() {
      try {
        const response = await get('api/ledger/accounts');
        this.accounts = response.data || [];
      } catch (error) {
        console.error('Error fetching accounts:', error);
      }
    },
    toggleCreateForm() {
      this.showCreateForm = !this.showCreateForm;
    },
    handleCreateSuccess() {
      this.toggleCreateForm();
      this.fetchJournalEntries();
    },
    async fetchJournalEntries() {
      this.loading = true;
      this.error = null;

      try {
        let url = 'api/ledger/journal/entries';
        const params = {};

        if (this.startDate && this.endDate) {
          params.start_date = this.startDate;
          params.end_date = this.endDate;
        }

        const response = await get(url, params);
        this.journalEntries = response.data || [];
      } catch (err) {
        console.error('Error fetching journal entries:', err);
        this.error = `Failed to load journal entries: ${err.message}`;
      } finally {
        this.loading = false;
      }
    },
    
    async deleteEntry(entryId) {
      if (!confirm('Are you sure you want to delete this journal entry?')) {
        return;
      }
      
      try {
        await del(`api/ledger/journal/entries/${entryId}`);
        this.fetchJournalEntries();
      } catch (err) {
        console.error('Error deleting journal entry:', err);
        alert(`Failed to delete entry: ${err.message}`);
      }
    },
    
    // Transform the journal entry lines into a format that displays correctly in the table
    processEntryLines(lines) {
      return lines.map(line => {
        return {
          account_id: line.account_id,
          account_name: line.account_name,
          account_number: line.account_number,
          debit: line.type === 'debit' ? line.amount : null,
          credit: line.type === 'credit' ? line.amount : null
        };
      });
    },
    applyDateFilter() {
      if (!this.startDate || !this.endDate) {
        alert('Please select both start and end dates');
        return;
      }
      this.fetchJournalEntries();
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      }).format(date);
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value);
    },
    viewEntryDetails(entry) {
      // This function will be implemented later
      alert(`View details for entry #${entry.id}`);
    },
    editEntry(entry) {
      // This function will be implemented later
      alert(`Edit entry #${entry.id}`);
    },
    calculateEntryTotal(entry) {
      // Calculate total based on debits only
      return entry.lines.reduce((total, line) => {
        return total + (line.type === 'debit' ? parseFloat(line.amount) : 0);
      }, 0);
    }
  },
  mounted() {
    document.title = 'GeoFinance - Journal Entries';
    
    // Set default date range to current month
    const now = new Date();
    const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
    const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    
    this.startDate = firstDay.toISOString().split('T')[0];
    this.endDate = lastDay.toISOString().split('T')[0];
    
    this.fetchAccounts();
    this.fetchJournalEntries();
  }
}
</script>

<style scoped>
.journal {
  padding: 20px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.journal-controls {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.filters {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn-primary, .btn-filter {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-filter {
  background-color: #4285f4;
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

.btn-delete {
  background-color: #dc3545;
}

.journal-entries-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.journal-entries-header {
  display: flex;
  justify-content: space-between;
  font-weight: bold;
  padding: 10px;
  background-color: #f1f1f1;
  border-radius: 4px;
  width: 100%;
}

.journal-entry-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #fff;
  position: relative;
  width: 100%;
}

.journal-entry-row:hover {
  background-color: #f9f9f9;
}

.col-id {
  flex: 0 0 10%;
  text-align: center;
}

.col-date {
  flex: 0 0 20%;
  text-align: center;
}

.col-desc {
  flex: 0 0 30%;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 10px;
}

.col-total {
  flex: 0 0 20%;
  text-align: right;
}

.col-actions {
  flex: 0 0 20%;
  text-align: center;
  display: flex;
  justify-content: center;
  gap: 5px;
}

.entry-details-popup {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.popup-header {
  margin-bottom: 10px;
}

.entry-details-table {
  width: 100%;
  border-collapse: collapse;
}

.entry-details-table th, .entry-details-table td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.loading, .error, .no-entries {
  text-align: center;
  padding: 30px;
}

.error {
  color: #dc3545;
}
</style>
