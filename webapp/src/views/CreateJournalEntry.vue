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
                <select v-model="line.account_id" required class="form-control">
                  <option value="" disabled>Select an account</option>
                  <option v-for="account in accounts" :key="account.id" :value="account.id">
                    {{ account.number }} - {{ account.name }} ({{ account.type }})
                  </option>
                </select>
              </td>
              <td>
                <input type="number" v-model="line.amount" required class="form-control" step="0.01" min="0" />
              </td>
              <td>
                <div class="radio-group">
                  <label>
                    <input type="radio" :name="`type-${index}`" value="debit" v-model="line.type" />
                    Debit
                  </label>
                  <label>
                    <input type="radio" :name="`type-${index}`" value="credit" v-model="line.type" />
                    Credit
                  </label>
                </div>
              </td>
              <td>
                <button type="button" @click="removeLine(index)" class="btn btn-danger">Remove</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="button-container">
        <button type="button" @click="addLine" class="btn btn-secondary">Add Line</button>
        <div class="submit-buttons">
          <button type="submit" class="btn btn-primary">Submit</button>
          <button type="button" @click="$emit('cancel')" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import { buildApiUrl, getHeaders } from '../config/api';

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
    };
  },
  methods: {
    addLine() {
      this.lines.push({ account_id: "", amount: "", type: "debit" });
    },
    removeLine(index) {
      this.lines.splice(index, 1);
    },
    async submitJournalEntry() {
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
        
        const response = await fetch(buildApiUrl("api/ledger/journal/entries"), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          credentials: 'include'
        });
        
        if (!response.ok) {
          const error = await response.json();
          alert(`Error: ${error.message}`);
        } else {
          alert("Journal entry created successfully!");
          this.$emit('success');
        }
      } catch (error) {
        alert(`Error: ${error.message}`);
      }
    },
  },
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
</style>