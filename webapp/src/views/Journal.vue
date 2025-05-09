<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Journal Entries</h1>
    </div>

    <div v-if="showCreateForm">
      <CreateJournalEntry
        :accounts="accounts"
        @success="handleCreateSuccess"
        @cancel="toggleCreateForm"
      />
    </div>

    <div v-else>
      <div class="d-flex justify-content-between align-items-center flex-wrap mb-4 gap-controls">
        <button @click="toggleCreateForm" class="btn btn-primary">Create New Journal</button>
        
        <DateRangePicker
          v-model:startDate="startDate"
          v-model:endDate="endDate"
          @apply="fetchJournalEntries"
          :showPresets="true"
          applyButtonText="Filter Entries"
        />
      </div>

      <LoadingIndicator v-if="loading" message="Loading journal entries..." />
      
      <ErrorMessage
        v-else-if="error"
        :message="error"
        :retry="true"
        @retry="fetchJournalEntries"
      />

      <div v-else>
        <div class="table-responsive">
          <BaseTable
            v-if="journalEntries.length > 0"
            :columns="columns"
            :items="journalEntries"
            :hasActions="true"
          >
            <template #cell-date="{ value }">
              {{ formatDate(value) }}
            </template>
            
            <template #cell-total="{ item }">
              {{ formatCurrency(calculateEntryTotal(item)) }}
            </template>
            
            <template #actions="{ item }">
              <button @click="viewEntryDetails(item)" class="btn btn-primary btn-sm">View</button>
              <button @click="editEntry(item)" class="btn btn-warning btn-sm">Edit</button>
              <button @click="confirmDelete(item.id)" class="btn btn-danger btn-sm">Delete</button>
            </template>
            
            <template #no-data>
              <div class="text-center py-4 text-secondary">
                <p>No journal entries found.</p>
              </div>
            </template>
          </BaseTable>
        </div>
        
        <!-- Detailed view that appears on hover - could be moved to a separate component -->
        <div v-for="entry in journalEntries" :key="`detail-${entry.id}`">
          <div v-if="hoveredEntry === entry.id" class="entry-details-popup">
            <div class="card-header">
              <h4 class="card-title">Entry #{{ entry.id }} - {{ formatDate(entry.date) }}</h4>
              <div>{{ entry.description }}</div>
            </div>
            
            <div class="card-body">
              <BaseTable
                :columns="detailColumns"
                :items="processEntryLines(entry.lines)"
                :hasActions="false"
                class="table table-striped"
              >
                <template #cell-debit="{ value }">
                  {{ value ? formatCurrency(value) : '' }}
                </template>
                <template #cell-credit="{ value }">
                  {{ value ? formatCurrency(value) : '' }}
                </template>
              </BaseTable>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <ConfirmDialog
      :show="showConfirmDialog"
      title="Confirm Delete"
      :message="confirmMessage"
      confirmText="Delete"
      :danger="true"
      @confirm="deleteEntry"
      @cancel="cancelDelete"
    />
  </div>
</template>

<script>
import CreateJournalEntry from './CreateJournalEntry.vue';
import DateRangePicker from '../components/DateRangePicker.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';
import ErrorMessage from '../components/ErrorMessage.vue';
import BaseTable from '../components/BaseTable.vue';
import ConfirmDialog from '../components/ConfirmDialog.vue';
import { get, del } from '../services/apiService';
import { formatCurrency, formatDate } from '../services/formatters';

export default {
  name: 'JournalView',
  components: {
    CreateJournalEntry,
    DateRangePicker,
    LoadingIndicator,
    ErrorMessage,
    BaseTable,
    ConfirmDialog
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
      showConfirmDialog: false,
      entryToDelete: null,
      confirmMessage: '',
      columns: [
        { key: 'id', label: 'Entry #' },
        { key: 'date', label: 'Date' },
        { key: 'description', label: 'Description' },
        { key: 'total', label: 'Total Amount', format: 'currency' }
      ],
      detailColumns: [
        { key: 'account_name', label: 'Account' },
        { key: 'debit', label: 'Debit' },
        { key: 'credit', label: 'Credit' }
      ]
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
    
    confirmDelete(entryId) {
      this.entryToDelete = entryId;
      this.confirmMessage = `Are you sure you want to delete journal entry #${entryId}?`;
      this.showConfirmDialog = true;
    },
    
    cancelDelete() {
      this.showConfirmDialog = false;
      this.entryToDelete = null;
    },
    
    async deleteEntry() {
      try {
        await del(`api/ledger/journal/entries/${this.entryToDelete}`);
        this.fetchJournalEntries();
      } catch (err) {
        console.error('Error deleting journal entry:', err);
        this.error = `Failed to delete entry: ${err.message}`;
      } finally {
        this.showConfirmDialog = false;
        this.entryToDelete = null;
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
    
    formatDate,
    formatCurrency,
    
    viewEntryDetails(entry) {
      // Toggle hover state to show detail view
      this.hoveredEntry = this.hoveredEntry === entry.id ? null : entry.id;
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
/* Component-specific styles */
.gap-controls {
  gap: 15px;
}

.entry-details-popup {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 800px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  z-index: var(--z-index-modal);
  box-shadow: var(--shadow-md);
}
</style>
