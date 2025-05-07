<template>
  <div class="journal">
    <h1>Journal Entries</h1>
    <div class="journal-controls">
      <button @click="createNewEntry" class="btn-primary">Create New Journal Entry</button>
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
      
      <div v-else class="journal-entries">
        <div v-for="entry in journalEntries" :key="entry.id" class="journal-entry">
          <div class="entry-header">
            <div>
              <h3>Entry #{{ entry.id }}</h3>
              <p class="entry-date">{{ formatDate(entry.date) }}</p>
            </div>
            <div class="entry-actions">
              <button @click="viewEntryDetails(entry)" class="btn-small">View</button>
              <button @click="editEntry(entry)" class="btn-small btn-edit">Edit</button>
            </div>
          </div>
          
          <div class="entry-description">
            <strong>Description:</strong> {{ entry.description }}
          </div>
          
          <table class="entry-lines">
            <thead>
              <tr>
                <th>Account</th>
                <th>Debit</th>
                <th>Credit</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(line, index) in entry.lines" :key="index">
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
</template>

<script>
import { buildApiUrl } from '../config/api';
import { getAuthHeaders } from '../services/authService';

export default {
  name: 'JournalView',
  data() {
    return {
      journalEntries: [],
      loading: true,
      error: null,
      startDate: '',
      endDate: ''
    }
  },
  methods: {
    async fetchJournalEntries() {
      this.loading = true;
      this.error = null;
      
      try {
        let url = 'api/ledger/journal';
        const params = new URLSearchParams();
        
        if (this.startDate && this.endDate) {
          params.append('start_date', this.startDate);
          params.append('end_date', this.endDate);
        }

        const fullUrl = buildApiUrl(`${url}?${params.toString()}`);
        console.log('Fetching journal entries from:', fullUrl);
        
        const response = await fetch(fullUrl, {
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
          throw new Error(data.message || 'Failed to fetch journal entries');
        }
        
        // Make sure data is an array
        if (!Array.isArray(data)) {
          console.warn('Response is not an array, using empty array instead');
          this.journalEntries = [];
          return;
        }
        
        console.log('Parsed data:', data);
        this.journalEntries = data;
      } catch (err) {
        console.error('Error fetching journal entries:', err);
        this.error = `Failed to load journal entries: ${err.message}`;
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
    formatDate(dateString) {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      }).format(date);
    },
    createNewEntry() {
      // This function will be implemented later
      alert('Create new journal entry feature will be added soon');
    },
    viewEntryDetails(entry) {
      // This function will be implemented later
      alert(`View details for entry #${entry.id}`);
    },
    editEntry(entry) {
      // This function will be implemented later
      alert(`Edit entry #${entry.id}`);
    },
    applyDateFilter() {
      if (!this.startDate || !this.endDate) {
        alert('Please select both start and end dates');
        return;
      }
      this.fetchJournalEntries();
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
    
    this.fetchJournalEntries();
  }
}
</script>

<style scoped>
.journal {
  padding: 20px;
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

.journal-entries {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.journal-entry {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  background-color: #f9f9f9;
}

.entry-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.entry-date {
  color: #666;
  margin-top: 5px;
}

.entry-description {
  margin-bottom: 15px;
}

.entry-lines {
  width: 100%;
  border-collapse: collapse;
}

.entry-lines th, .entry-lines td {
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