<template>
  <div class="create-journal-entry">
    <h2>Create New Journal Entry</h2>
    <form @submit.prevent="submitJournalEntry" class="form-container">
      <div class="form-group">
        <label for="description">Description:</label>
        <input type="text" id="description" v-model="description" required class="form-control" />
      </div>

      <div class="table-container">
        <table class="entry-lines-table">
          <thead>
            <tr>
              <th>Account</th>
              <th>Amount</th>
              <th>Type</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(line, index) in lines" :key="index">
              <td>
                <select 
                  v-model="line.account_id" 
                  required 
                  class="form-control"
                  @change="updateLineType(index)"
                >
                  <option value="" disabled>Select an account</option>
                  <option v-for="account in accounts" :key="account.id" :value="account.id">
                    {{ account.number }} - {{ account.name }} ({{ account.type }})
                  </option>
                </select>
              </td>
              <td>
                <input 
                  type="number" 
                  v-model="line.amount" 
                  required 
                  class="form-control" 
                  step="0.01" 
                  min="0"
                  @input="validateBalance"
                />
              </td>
              <td>
                <div class="radio-group">
                  <label>
                    <input type="radio" :name="`type-${index}`" value="debit" v-model="line.type" @change="validateBalance" />
                    Debit
                  </label>
                  <label>
                    <input type="radio" :name="`type-${index}`" value="credit" v-model="line.type" @change="validateBalance" />
                    Credit
                  </label>
                </div>
              </td>
              <td>
                <button type="button" @click="removeLine(index)" class="btn btn-danger">Remove</button>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td colspan="2"></td>
              <td>
                <div class="totals">
                  <div>Total Debits: {{ formatCurrency(totalDebits) }}</div>
                  <div>Total Credits: {{ formatCurrency(totalCredits) }}</div>
                </div>
              </td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>

      <div class="balance-status" :class="{ 'balanced': isBalanced, 'unbalanced': !isBalanced }">
        <span v-if="isBalanced">Journal entry is balanced</span>
        <span v-else>Journal entry is not balanced. The difference is {{ formatCurrency(Math.abs(totalDebits - totalCredits)) }}</span>
      </div>

      <div class="button-container">
        <button type="button" @click="addLine" class="btn btn-secondary">Add Line</button>
        <div class="submit-buttons">
          <button type="submit" class="btn btn-primary" :disabled="!isBalanced">Submit</button>
          <button type="button" @click="$emit('cancel')" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import { post } from '../services/apiService';

export default {
  props: {
    accounts: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      description: "",
      lines: [
        { account_id: "", amount: "", type: "debit" },
        { account_id: "", amount: "", type: "credit" },
      ],
      totalDebits: 0,
      totalCredits: 0,
      isBalanced: false,
    };
  },
  methods: {
    addLine() {
      this.lines.push({ account_id: "", amount: "", type: "debit" });
    },
    removeLine(index) {
      this.lines.splice(index, 1);
      this.validateBalance();
    },
    getAccountById(id) {
      if (!id) return null;
      // Convert id to number before comparison to ensure proper matching
      const accountId = parseInt(id);
      return this.accounts.find(account => account.id === accountId);
    },
    updateLineType(index) {
      const line = this.lines[index];
      if (!line.account_id) return;
      
      const account = this.getAccountById(line.account_id);
      if (!account) return;
      
      // Set default type based on account type
      // For asset and expense accounts, debit increases the balance
      // For liability, equity, and income accounts, credit increases the balance
      if (account.type === 'asset' || account.type === 'expense') {
        line.type = 'debit';
      } else if (account.type === 'liability' || account.type === 'income' || account.type === 'equity') {
        line.type = 'credit';
      }
      
      this.validateBalance();
    },
    validateBalance() {
      // Calculate total debits and credits
      let totalDebits = 0;
      let totalCredits = 0;
      
      this.lines.forEach(line => {
        if (line.amount && line.type) {
          const amount = parseFloat(line.amount) || 0;
          if (line.type === 'debit') {
            totalDebits += amount;
          } else {
            totalCredits += amount;
          }
        }
      });
      
      this.totalDebits = totalDebits;
      this.totalCredits = totalCredits;
      
      // Check if the entry is balanced
      this.isBalanced = Math.abs(totalDebits - totalCredits) < 0.001; // Use a small epsilon for floating-point comparison
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value);
    },
    async submitJournalEntry() {
      if (!this.isBalanced) {
        alert("Journal entry must be balanced before submission.");
        return;
      }
      
      try {
        // Format the payload according to the expected structure
        const payload = {
          description: this.description,
          lines: this.lines.map(line => ({
            account_id: parseInt(line.account_id),
            amount: parseFloat(line.amount),
            type: line.type
          }))
        };
        
        const response = await post("api/ledger/journal/entries", payload);
        alert("Journal entry created successfully!");
        this.$emit('success');
      } catch (error) {
        alert(`Error: ${error.response?.data?.message || error.message}`);
      }
    },
  },
  mounted() {
    // Initialize balance validation
    this.validateBalance();
  }
};
</script>

<style scoped>
.create-journal-entry {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-control {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 100%;
}

.table-container {
  overflow-x: auto;
}

.entry-lines-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

.entry-lines-table th, .entry-lines-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.radio-group {
  display: flex;
  gap: 15px;
}

.radio-group label {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 5px;
}

.button-container {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.submit-buttons {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.totals {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-weight: bold;
}

.balance-status {
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
  text-align: center;
  font-weight: bold;
}

.balanced {
  background-color: #d4edda;
  color: #155724;
}

.unbalanced {
  background-color: #f8d7da;
  color: #721c24;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>