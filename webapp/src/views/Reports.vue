<template>
  <div class="reports">
    <h1>Financial Reports</h1>
    
    <div class="reports-controls">
      <div class="report-selector">
        <label for="report-type">Report Type:</label>
        <select id="report-type" v-model="selectedReportType">
          <option value="balance-sheet">Balance Sheet</option>
          <option value="income-statement">Income Statement</option>
          <option value="trial-balance">Trial Balance</option>
          <option value="ledger-balance">Ledger Balance</option> <!-- Added Ledger Balance option -->
        </select>
      </div>
      
      <div class="date-filters">
        <div class="date-range">
          <label for="as-of-date">As of Date:</label>
          <input type="date" id="as-of-date" v-model="asOfDate" :disabled="!isBalanceSheetOrTrial">
        </div>
        
        <div class="date-range" v-if="!isBalanceSheetOrTrial">
          <label for="start-date">Start Date:</label>
          <input type="date" id="start-date" v-model="startDate">
        </div>
        
        <div class="date-range" v-if="!isBalanceSheetOrTrial">
          <label for="end-date">End Date:</label>
          <input type="date" id="end-date" v-model="endDate">
        </div>
      </div>
      
      <button @click="generateReport" class="btn-primary">Generate Report</button>
    </div>
    
    <div v-if="loading" class="loading">
      <p>Generating report...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="generateReport" class="btn-primary">Retry</button>
    </div>
    
    <div v-else-if="reportData || ledgerBalance" class="report-container">
      <!-- Balance Sheet Report -->
      <div v-if="selectedReportType === 'balance-sheet'" class="report">
        <h2>Balance Sheet</h2>
        <h3>As of {{ formatDate(asOfDate) }}</h3>

        <div class="report-section">
          <h4>Assets</h4>
          <div v-for="(account, index) in reportData.asset_accounts" :key="'asset-'+index" class="report-line">
            <span class="account-name">{{ account.account_name }} ({{ account.account_number }})</span>
            <span class="account-value">{{ formatCurrency(account.balance) }}</span>
          </div>
          <div class="report-total">
            <span>Total Assets</span>
            <span>{{ formatCurrency(reportData.total_assets) }}</span>
          </div>
        </div>

        <div class="report-section">
          <h4>Liabilities</h4>
          <div v-for="(account, index) in reportData.liability_accounts" :key="'liability-'+index" class="report-line">
            <span class="account-name">{{ account.account_name }} ({{ account.account_number }})</span>
            <span class="account-value">{{ formatCurrency(account.balance) }}</span>
          </div>
          <div class="report-total">
            <span>Total Liabilities</span>
            <span>{{ formatCurrency(reportData.total_liabilities) }}</span>
          </div>
        </div>

        <div class="report-section">
          <h4>Equity</h4>
          <div v-for="(account, index) in reportData.equity_accounts" :key="'equity-'+index" class="report-line">
            <span class="account-name">{{ account.account_name }} ({{ account.account_number || 'N/A' }})</span>
            <span class="account-value">{{ formatCurrency(account.balance) }}</span>
          </div>
          <div class="report-total">
            <span>Total Equity</span>
            <span>{{ formatCurrency(reportData.total_equity) }}</span>
          </div>
        </div>
      </div>
      
      <!-- Income Statement Report -->
      <div v-else-if="selectedReportType === 'income-statement'" class="report">
        <h2>Income Statement</h2>
        <h3>{{ formatDate(startDate) }} - {{ formatDate(endDate) }}</h3>

        <div class="report-section">
          <h4>Income</h4>
          <div v-for="(account, index) in reportData.income_accounts" :key="'income-'+index" class="report-line">
            <span class="account-name">{{ account.account_name }} ({{ account.account_number }})</span>
            <span class="account-value">{{ formatCurrency(account.balance) }}</span>
          </div>
          <div class="report-total">
            <span>Total Income</span>
            <span>{{ formatCurrency(reportData.total_income) }}</span>
          </div>
        </div>

        <div class="report-section">
          <h4>Expenses</h4>
          <div v-for="(account, index) in reportData.expense_accounts" :key="'expense-'+index" class="report-line">
            <span class="account-name">{{ account.account_name }} ({{ account.account_number }})</span>
            <span class="account-value">{{ formatCurrency(account.balance) }}</span>
          </div>
          <div class="report-total">
            <span>Total Expenses</span>
            <span>{{ formatCurrency(reportData.total_expenses) }}</span>
          </div>
        </div>

        <div class="net-income">
          <span>Net Income</span>
          <span>{{ formatCurrency(reportData.net_income) }}</span>
        </div>
      </div>
      
      <!-- Trial Balance Report -->
      <div v-else-if="selectedReportType === 'trial-balance'" class="report">
        <h2>Trial Balance</h2>
        <h3>{{ formatDate(asOfDate) }}</h3>

        <table class="trial-balance-table">
          <thead>
            <tr>
              <th>Account Name</th>
              <th>Account Number</th>
              <th>Account Type</th>
              <th>Debit Balance</th>
              <th>Credit Balance</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(account, index) in reportData.trial_balance" :key="'trial-'+index">
              <td>{{ account.account_name }}</td>
              <td>{{ account.account_number }}</td>
              <td>{{ account.account_type }}</td>
              <td>{{ formatCurrency(account.debit_balance) }}</td>
              <td>{{ formatCurrency(account.credit_balance) }}</td>
            </tr>
          </tbody>
        </table>

        <div class="report-totals">
          <div>
            <strong>Total Debits:</strong> {{ formatCurrency(reportData.total_debits) }}
          </div>
          <div>
            <strong>Total Credits:</strong> {{ formatCurrency(reportData.total_credits) }}
          </div>
        </div>

        <div v-if="reportData.balanced" class="balanced-message">
          <p>The trial balance is balanced.</p>
        </div>
        <div v-else class="unbalanced-message">
          <p>The trial balance is not balanced.</p>
        </div>
      </div>
      
      <!-- Ledger Balance Report -->
      <div v-else-if="selectedReportType === 'ledger-balance'" class="report">
        <h2>Ledger Balance</h2>
        <ul>
          <li v-for="account in ledgerBalance" :key="account.account_id">
            <strong>{{ account.account_name }} ({{ account.account_number }})</strong>: {{ formatCurrency(account.balance) }}
          </li>
        </ul>
      </div>
      
      <!-- Other report types would be implemented similarly -->
      <div v-else class="report-placeholder">
        <p>{{ selectedReportType }} report implementation coming soon.</p>
      </div>
      
      <div class="report-actions">
        <button @click="exportReport" class="btn-export">Export as PDF</button>
        <button @click="printReport" class="btn-print">Print Report</button>
      </div>
    </div>
    
    <div v-else class="report-instructions">
      <p>Select a report type and date range, then click "Generate Report" to view financial data.</p>
    </div>
  </div>
</template>

<script>
import { buildApiUrl } from '../config/api';
import { getAuthHeaders } from '../services/authService';

export default {
  name: 'ReportsView',
  data() {
    return {
      selectedReportType: 'balance-sheet',
      asOfDate: '',
      startDate: '',
      endDate: '',
      reportData: null,
      ledgerBalance: null, // Added ledger balance data
      loading: false,
      error: null
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
        if (this.isBalanceSheetOrTrial && this.selectedReportType !== 'ledger-balance') {
          params.append('as_of_date', this.asOfDate);
        } else if (this.selectedReportType !== 'ledger-balance') {
          params.append('start_date', this.startDate);
          params.append('end_date', this.endDate);
        }
        
        const fullUrl = buildApiUrl(`${url}?${params.toString()}`);
        console.log('Fetching report from:', fullUrl);
        
        const response = await fetch(fullUrl, {
          headers: getAuthHeaders(),
          credentials: 'include' // Ensure cookies are sent with the request
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', Object.fromEntries([...response.headers.entries()]));
        
        const text = await response.text();
        console.log('Raw response:', text);
        
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
.reports {
  padding: 20px;
}

.reports-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 30px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.report-selector, .date-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
}

.date-range {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

select, input[type="date"] {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 200px;
}

label {
  font-weight: bold;
  color: #555;
}

.btn-primary {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: auto;
}

.report-container {
  margin-top: 20px;
}

.report {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
}

.report h2 {
  font-size: 24px;
  margin-bottom: 5px;
}

.report h3 {
  font-size: 16px;
  color: #666;
  margin-bottom: 20px;
}

.report-section {
  margin-bottom: 25px;
}

.report-section h4 {
  font-size: 18px;
  border-bottom: 2px solid #42b983;
  padding-bottom: 5px;
  margin-bottom: 15px;
}

.report-line {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px dotted #ddd;
}

.report-total {
  display: flex;
  justify-content: space-between;
  font-weight: bold;
  padding: 12px 0;
  margin-top: 10px;
  border-top: 1px solid #666;
}

.net-income {
  display: flex;
  justify-content: space-between;
  font-weight: bold;
  font-size: 18px;
  padding: 15px 0;
  margin-top: 20px;
  border-top: 2px solid #42b983;
}

.trial-balance-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.trial-balance-table th, .trial-balance-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.trial-balance-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.report-totals {
  margin-top: 20px;
}

.balanced-message {
  color: #42b983;
  font-weight: bold;
  margin-top: 20px;
}

.unbalanced-message {
  color: #dc3545;
  font-weight: bold;
  margin-top: 20px;
}

.report-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 25px;
}

.btn-export, .btn-print {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-export {
  background-color: #4285f4;
  color: white;
}

.btn-print {
  background-color: #f8f9fa;
  color: #333;
  border: 1px solid #ddd;
}

.loading, .error, .report-instructions, .report-placeholder {
  text-align: center;
  padding: 30px;
}

.error {
  color: #dc3545;
}

.report-instructions {
  font-style: italic;
  color: #666;
}

@media print {
  .reports-controls, .report-actions {
    display: none;
  }
  
  .report {
    box-shadow: none;
    padding: 0;
  }
}
</style>