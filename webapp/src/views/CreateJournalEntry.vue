<template>
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">Create New Journal Entry</h2>
    </div>
    <div class="card-body">
      <form @submit.prevent="submitJournalEntry">
        <div class="form-group mb-3">
          <label for="description" class="form-label">Description:</label>
          <input type="text" id="description" v-model="description" required class="form-control" />
        </div>

        <div class="table-responsive">
          <table class="table table-striped">
            <thead class="table-header">
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
                    class="form-select"
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
                  <div class="form-check-inline">
                    <label class="form-check-label me-3">
                      <input type="radio" class="form-check-input" :name="`type-${index}`" value="debit" v-model="line.type" @change="validateBalance" />
                      Debit
                    </label>
                    <label class="form-check-label">
                      <input type="radio" class="form-check-input" :name="`type-${index}`" value="credit" v-model="line.type" @change="validateBalance" />
                      Credit
                    </label>
                  </div>
                </td>
                <td>
                  <button type="button" @click="removeLine(index)" class="btn btn-danger btn-sm">Remove</button>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="2"></td>
                <td>
                  <div class="d-flex flex-column">
                    <div>Total Debits: {{ formatCurrency(totalDebits) }}</div>
                    <div>Total Credits: {{ formatCurrency(totalCredits) }}</div>
                  </div>
                </td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>

        <div class="alert" :class="isBalanced ? 'alert-success' : 'alert-danger'">
          <span v-if="isBalanced">Journal entry is balanced</span>
          <span v-else>Journal entry is not balanced. The difference is {{ formatCurrency(Math.abs(totalDebits - totalCredits)) }}</span>
        </div>

        <div class="d-flex justify-content-between mt-3">
          <button type="button" @click="addLine" class="btn btn-secondary">Add Line</button>
          <div class="d-flex gap-2">
            <button type="submit" class="btn btn-primary" :disabled="!isBalanced">Submit</button>
            <button type="button" @click="$emit('cancel')" class="btn btn-outline-secondary">Cancel</button>
          </div>
        </div>
      </form>
    </div>
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