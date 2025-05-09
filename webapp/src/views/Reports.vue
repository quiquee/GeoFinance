<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Financial Reports</h1>
    </div>
    
    <div class="card mb-4">
      <div class="card-body d-flex flex-wrap gap-4 align-items-end">
        <div class="form-group">
          <label for="report-type" class="form-label">Report Type:</label>
          <select id="report-type" v-model="selectedReportType" class="form-select">
            <option value="balance-sheet">Balance Sheet</option>
            <option value="income-statement">Income Statement</option>
            <option value="trial-balance">Trial Balance</option>
            <option value="ledger-balance">Ledger Balance</option>
          </select>
        </div>
        
        <!-- Use DateRangePicker with single date mode for balance sheet and trial balance -->
        <div v-if="isBalanceSheetOrTrial" class="form-group">
          <label for="as-of-date" class="form-label">As of Date:</label>
          <input type="date" id="as-of-date" v-model="asOfDate" class="form-control">
        </div>
        
        <!-- Use DateRangePicker for other reports that need date ranges -->
        <DateRangePicker
          v-else
          v-model:startDate="startDate"
          v-model:endDate="endDate"
          :showApplyButton="false"
        />
        
        <button @click="generateReport" class="btn btn-primary ms-auto">Generate Report</button>
      </div>
    </div>
    
    <LoadingIndicator v-if="loading" message="Generating report..." />
    
    <ErrorMessage
      v-else-if="error"
      :message="error"
      :retry="true"
      @retry="generateReport"
    />
    
    <div v-else-if="reportData || ledgerBalance" class="card">
      <div class="card-body">
        <!-- Balance Sheet Report -->
        <div v-if="selectedReportType === 'balance-sheet'" class="report">
          <div class="text-center mb-4">
            <h2 class="mb-1">Balance Sheet</h2>
            <h3 class="text-secondary">As of {{ formatDate(asOfDate) }}</h3>
          </div>

          <div class="row">
            <!-- Assets column -->
            <div class="col-md-6 mb-4">
              <h4 class="report-section-title">Assets</h4>
              <BaseTable
                :columns="assetColumns"
                :items="reportData.asset_accounts"
                :hasActions="false"
              >
                <template #cell-balance="{ value }">
                  {{ formatCurrency(value) }}
                </template>
              </BaseTable>
              <div class="d-flex justify-content-between fw-bold py-3 border-top mt-2">
                <span>Total Assets</span>
                <span>{{ formatCurrency(reportData.total_assets) }}</span>
              </div>
            </div>
            
            <!-- Liabilities and Equity column -->
            <div class="col-md-6">
              <div class="mb-4">
                <h4 class="report-section-title">Liabilities</h4>
                <BaseTable
                  :columns="liabilityColumns"
                  :items="reportData.liability_accounts"
                  :hasActions="false"
                >
                  <template #cell-balance="{ value }">
                    {{ formatCurrency(value) }}
                  </template>
                </BaseTable>
                <div class="d-flex justify-content-between fw-bold py-3 border-top mt-2">
                  <span>Total Liabilities</span>
                  <span>{{ formatCurrency(reportData.total_liabilities) }}</span>
                </div>
              </div>

              <div class="mb-4">
                <h4 class="report-section-title">Equity</h4>
                <BaseTable
                  :columns="equityColumns"
                  :items="reportData.equity_accounts"
                  :hasActions="false"
                >
                  <template #cell-balance="{ value }">
                    {{ formatCurrency(value) }}
                  </template>
                </BaseTable>
                <div class="d-flex justify-content-between fw-bold py-3 border-top mt-2">
                  <span>Total Equity</span>
                  <span>{{ formatCurrency(reportData.total_equity) }}</span>
                </div>
              </div>
              
              <!-- Total Liabilities and Equity -->
              <div class="d-flex justify-content-between fw-bold fs-5 py-3 border-top mt-2">
                <span>Total Liabilities and Equity</span>
                <span>{{ formatCurrency(parseFloat(reportData.total_liabilities) + parseFloat(reportData.total_equity)) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Income Statement Report -->
        <div v-else-if="selectedReportType === 'income-statement'" class="report">
          <div class="text-center mb-4">
            <h2 class="mb-1">Income Statement</h2>
            <h3 class="text-secondary">{{ formatDate(startDate) }} - {{ formatDate(endDate) }}</h3>
          </div>

          <div class="mb-4">
            <h4 class="report-section-title">Income</h4>
            <BaseTable
              :columns="incomeColumns"
              :items="reportData.income_accounts"
              :hasActions="false"
            >
              <template #cell-balance="{ value }">
                {{ formatCurrency(value) }}
              </template>
            </BaseTable>
            <div class="d-flex justify-content-between fw-bold py-3 border-top mt-2">
              <span>Total Income</span>
              <span>{{ formatCurrency(reportData.total_income) }}</span>
            </div>
          </div>

          <div class="mb-4">
            <h4 class="report-section-title">Expenses</h4>
            <BaseTable
              :columns="expenseColumns"
              :items="reportData.expense_accounts"
              :hasActions="false"
            >
              <template #cell-balance="{ value }">
                {{ formatCurrency(value) }}
              </template>
            </BaseTable>
            <div class="d-flex justify-content-between fw-bold py-3 border-top mt-2">
              <span>Total Expenses</span>
              <span>{{ formatCurrency(reportData.total_expenses) }}</span>
            </div>
          </div>

          <div class="d-flex justify-content-between fw-bold fs-5 py-3 border-top mt-4">
            <span>Net Income</span>
            <span>{{ formatCurrency(reportData.net_income) }}</span>
          </div>
        </div>
        
        <!-- Trial Balance Report -->
        <div v-else-if="selectedReportType === 'trial-balance'" class="report">
          <div class="text-center mb-4">
            <h2 class="mb-1">Trial Balance</h2>
            <h3 class="text-secondary">{{ formatDate(asOfDate) }}</h3>
          </div>

          <BaseTable
            :columns="trialBalanceColumns"
            :items="reportData.trial_balance"
            :hasActions="false"
          >
            <template #cell-debit_balance="{ value }">
              {{ formatCurrency(value) }}
            </template>
            <template #cell-credit_balance="{ value }">
              {{ formatCurrency(value) }}
            </template>
          </BaseTable>

          <div class="mt-4">
            <div class="fw-bold">
              Total Debits: {{ formatCurrency(reportData.total_debits) }}
            </div>
            <div class="fw-bold">
              Total Credits: {{ formatCurrency(reportData.total_credits) }}
            </div>
          </div>

          <div v-if="reportData.balanced" class="alert alert-success mt-3">
            <p class="mb-0">The trial balance is balanced.</p>
          </div>
          <div v-else class="alert alert-danger mt-3">
            <p class="mb-0">The trial balance is not balanced.</p>
          </div>
        </div>
        
        <!-- Ledger Balance Report -->
        <div v-else-if="selectedReportType === 'ledger-balance'" class="report">
          <div class="text-center mb-4">
            <h2 class="mb-1">Ledger Balance</h2>
          </div>
          <BaseTable
            :columns="ledgerBalanceColumns"
            :items="ledgerBalance"
            :hasActions="false"
          >
            <template #cell-balance="{ value }">
              {{ formatCurrency(value) }}
            </template>
          </BaseTable>
        </div>
        
        <!-- Other report types would be implemented similarly -->
        <div v-else class="text-center py-5 text-secondary">
          <p class="mb-0">{{ selectedReportType }} report implementation coming soon.</p>
        </div>
        
        <div class="d-flex justify-content-end gap-3 mt-4">
          <button @click="exportReport" class="btn btn-secondary">Export as PDF</button>
          <button @click="printReport" class="btn btn-light border">Print Report</button>
        </div>
      </div>
    </div>
    
    <div v-else class="card">
      <div class="card-body text-center py-5 text-secondary">
        <p class="mb-0">Select a report type and date range, then click "Generate Report" to view financial data.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { buildApiUrl } from '../config/api';
import { getAuthHeaders } from '../services/authService';
import { formatCurrency, formatDate } from '../services/formatters';
import DateRangePicker from '../components/DateRangePicker.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';
import ErrorMessage from '../components/ErrorMessage.vue';
import BaseTable from '../components/BaseTable.vue';

export default {
  name: 'ReportsView',
  components: {
    DateRangePicker,
    LoadingIndicator,
    ErrorMessage,
    BaseTable
  },
  data() {
    return {
      selectedReportType: 'balance-sheet',
      asOfDate: '',
      startDate: '',
      endDate: '',
      reportData: null,
      ledgerBalance: null,
      loading: false,
      error: null,
      // Column definitions for different report tables
      assetColumns: [
        { key: 'account_name', label: 'Account Name' },
        { key: 'account_number', label: 'Account Number' },
        { key: 'balance', label: 'Balance', format: 'currency' }
      ],
      liabilityColumns: [
        { key: 'account_name', label: 'Account Name' },
        { key: 'account_number', label: 'Account Number' },
        { key: 'balance', label: 'Balance', format: 'currency' }
      ],
      equityColumns: [
        { key: 'account_name', label: 'Account Name' },
        { key: 'account_number', label: 'Account Number' },
        { key: 'balance', label: 'Balance', format: 'currency' }
      ],
      incomeColumns: [
        { key: 'account_name', label: 'Account Name' },
        { key: 'account_number', label: 'Account Number' },
        { key: 'balance', label: 'Balance', format: 'currency' }
      ],
      expenseColumns: [
        { key: 'account_name', label: 'Account Name' },
        { key: 'account_number', label: 'Account Number' },
        { key: 'balance', label: 'Balance', format: 'currency' }
      ],
      trialBalanceColumns: [
        { key: 'account_name', label: 'Account Name' },
        { key: 'account_number', label: 'Account Number' },
        { key: 'account_type', label: 'Account Type' },
        { key: 'debit_balance', label: 'Debit Balance', format: 'currency' },
        { key: 'credit_balance', label: 'Credit Balance', format: 'currency' }
      ],
      ledgerBalanceColumns: [
        { key: 'account_name', label: 'Account Name' },
        { key: 'account_number', label: 'Account Number' },
        { key: 'balance', label: 'Balance', format: 'currency' }
      ]
    }
  },
  computed: {
    isBalanceSheetOrTrial() {
      return this.selectedReportType === 'balance-sheet' || this.selectedReportType === 'trial-balance';
    }
  },
  methods: {
    async generateReport() {
      this.loading = true;
      this.error = null;
      
      try {
        let url;
        if (this.selectedReportType === 'ledger-balance') {
          url = 'api/ledger/balance';
        } else {
          url = `api/ledger/${this.selectedReportType}`;
        }

        const params = new URLSearchParams();
        if (this.isBalanceSheetOrTrial ) {
          params.append('as_of_date', this.asOfDate);
        } else {
          params.append('start_date', this.startDate);
          params.append('end_date', this.endDate);
        }
        
        const fullUrl = buildApiUrl(`${url}?${params.toString()}`);
        
        const response = await fetch(fullUrl, {
          headers: getAuthHeaders(),
          credentials: 'include' // Ensure cookies are sent with the request
        });
        
        const text = await response.text();
        
        if (!text) {
          throw new Error('Empty response from server');
        }
        
        let data;
        try {
          data = JSON.parse(text);
        } catch (parseError) {
          console.error('Error parsing JSON:', parseError);
          throw new Error('Invalid JSON response from server');
        }
        
        if (!response.ok) {
          throw new Error(data.message || `Failed to generate ${this.selectedReportType} report`);
        }
        
        if (this.selectedReportType === 'ledger-balance') {
          this.ledgerBalance = data; // Store ledger balance data
        } else {
          this.reportData = data;
        }
      } catch (err) {
        console.error('Error generating report:', err);
        this.error = `Failed to generate report: ${err.message}`;
      } finally {
        this.loading = false;
      }
    },
    formatCurrency,
    formatDate,
    exportReport() {
      alert('Export to PDF feature will be implemented soon');
    },
    printReport() {
      window.print();
    }
  },
  mounted() {
    document.title = 'GeoFinance - Financial Reports';
    
    // Set default dates
    const now = new Date();
    this.asOfDate = now.toISOString().split('T')[0];
    
    // For income statement, default to current year
    const firstDayOfYear = new Date(now.getFullYear(), 0, 1);
    this.startDate = firstDayOfYear.toISOString().split('T')[0];
    this.endDate = now.toISOString().split('T')[0];
  },
  watch: {
    selectedReportType() {
      this.reportData = null;
      this.ledgerBalance = null; // Reset ledger balance data
    }
  }
}
</script>

<style scoped>
/* Component-specific styles */
.gap-4 {
  gap: 1rem;
}

.report-section-title {
  font-size: 1.125rem;
  border-bottom: 2px solid var(--color-primary);
  padding-bottom: 0.375rem;
  margin-bottom: 1rem;
}

@media print {
  .card {
    box-shadow: none;
    border: none;
  }
  
  .card-body {
    padding: 0;
  }
  
  .btn {
    display: none;
  }
}
</style>