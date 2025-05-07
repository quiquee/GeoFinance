// Journal Entries section functionality
async function loadJournalEntries() {
    try {
        // Load all journal entries
        const result = await apiFetch('/ledger/journal/entries');
        if (result.ok && result.data) {
            renderJournalEntriesList(result.data);
        } else {
            document.getElementById('journal-entries-list').innerHTML = '<p>Failed to load journal entries</p>';
        }
    } catch (error) {
        console.error('Error loading journal entries:', error);
        document.getElementById('journal-entries-list').innerHTML = '<p>Error loading journal entries</p>';
    }
}

function renderJournalEntriesList(entries) {
    const entriesList = document.getElementById('journal-entries-list');
    if (!entries || entries.length === 0) {
        entriesList.innerHTML = '<p>No journal entries found</p>';
        return;
    }
    
    let html = '<table class="data-table"><thead><tr>' +
        '<th>Date</th>' +
        '<th>Reference</th>' +
        '<th>Description</th>' +
        '<th>Total Debits</th>' +
        '<th>Total Credits</th>' +
        '<th>Actions</th>' +
        '</tr></thead><tbody>';
    
    entries.forEach(entry => {
        // Calculate total debits and credits from the entry lines
        let totalDebits = 0;
        let totalCredits = 0;
        
        if (entry.lines && entry.lines.length > 0) {
            entry.lines.forEach(line => {
                const amount = parseFloat(line.amount) || 0;
                if (line.type === 'debit') {
                    totalDebits += amount;
                } else if (line.type === 'credit') {
                    totalCredits += amount;
                }
            });
        }
        
        const date = new Date(entry.date).toLocaleDateString();
        html += `<tr>
            <td>${date}</td>
            <td>${entry.reference || ''}</td>
            <td>${entry.description}</td>
            <td class="amount">${totalDebits.toFixed(2)}</td>
            <td class="amount">${totalCredits.toFixed(2)}</td>
            <td>
                <button class="view-entry-btn" data-id="${entry.id}">View</button>
                <button class="delete-entry-btn" data-id="${entry.id}">Delete</button>
            </td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    entriesList.innerHTML = html;
    
    // Add event listeners for view and delete buttons
    document.querySelectorAll('.view-entry-btn').forEach(btn => {
        btn.addEventListener('click', () => viewJournalEntry(btn.getAttribute('data-id')));
    });
    
    document.querySelectorAll('.delete-entry-btn').forEach(btn => {
        btn.addEventListener('click', () => deleteJournalEntry(btn.getAttribute('data-id')));
    });
}

async function viewJournalEntry(entryId) {
    try {
        const result = await apiFetch(`/ledger/journal/entries/${entryId}`);
        if (!result.ok || !result.data) {
            alert('Failed to load journal entry details');
            return;
        }
        
        const entry = result.data;
        const date = new Date(entry.date).toLocaleDateString();
        
        // Calculate total debits and credits
        let totalDebits = 0;
        let totalCredits = 0;
        
        if (entry.lines && entry.lines.length > 0) {
            entry.lines.forEach(line => {
                const amount = parseFloat(line.amount) || 0;
                if (line.type === 'debit') {
                    totalDebits += amount;
                } else if (line.type === 'credit') {
                    totalCredits += amount;
                }
            });
        }
        
        const formHTML = `
            <div class="form-modal active" id="journal-view-modal">
                <div class="modal-content">
                    <h3>Journal Entry Details</h3>
                    <div class="entry-details">
                        <p><strong>Date:</strong> ${date}</p>
                        <p><strong>Reference:</strong> ${entry.reference || 'N/A'}</p>
                        <p><strong>Description:</strong> ${entry.description}</p>
                    </div>
                    <h4>Entry Lines</h4>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Account</th>
                                <th>Debit</th>
                                <th>Credit</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${entry.lines.map(line => `
                                <tr>
                                    <td>${line.account_number} - ${line.account_name}</td>
                                    <td class="amount">${line.type === 'debit' ? parseFloat(line.amount).toFixed(2) : ''}</td>
                                    <td class="amount">${line.type === 'credit' ? parseFloat(line.amount).toFixed(2) : ''}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                        <tfoot>
                            <tr>
                                <th>Total</th>
                                <th class="amount">${totalDebits.toFixed(2)}</th>
                                <th class="amount">${totalCredits.toFixed(2)}</th>
                            </tr>
                        </tfoot>
                    </table>
                    <div class="form-actions">
                        <button type="button" class="secondary" id="close-view-btn">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        // Append modal to the body
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = formHTML;
        document.body.appendChild(modalContainer.firstElementChild);
        
        // Add event listener
        document.getElementById('close-view-btn').addEventListener('click', closeViewModal);
        
    } catch (error) {
        console.error('Error loading journal entry details:', error);
        alert('An error occurred while loading journal entry details');
    }
}

function closeViewModal() {
    const modal = document.getElementById('journal-view-modal');
    if (modal) {
        modal.remove();
    }
}

function showNewJournalEntryForm() {
    // First, fetch all accounts to populate select dropdowns
    apiFetch('/ledger/accounts').then(result => {
        if (!result.ok || !result.data) {
            alert('Failed to load accounts');
            return;
        }
        
        const accounts = result.data;
        const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format
        
        const formHTML = `
            <div class="form-modal active" id="journal-form-modal">
                <div class="modal-content">
                    <h3>New Journal Entry</h3>
                    <form id="journal-form">
                        <div class="form-group">
                            <label for="journal-date">Date</label>
                            <input type="date" id="journal-date" value="${today}" required>
                        </div>
                        <div class="form-group">
                            <label for="journal-reference">Reference (Optional)</label>
                            <input type="text" id="journal-reference">
                        </div>
                        <div class="form-group">
                            <label for="journal-description">Description</label>
                            <input type="text" id="journal-description" required>
                        </div>
                        
                        <h4>Entry Lines</h4>
                        <div class="transaction-lines" id="transaction-lines">
                            <div class="transaction-line">
                                <select class="account-select" required>
                                    <option value="">Select Account</option>
                                    ${accounts.map(acc => `
                                        <option value="${acc.id}">${acc.number} - ${acc.name}</option>
                                    `).join('')}
                                </select>
                                <input type="number" class="debit-amount" step="0.01" placeholder="Debit">
                                <input type="number" class="credit-amount" step="0.01" placeholder="Credit">
                                <button type="button" class="remove-line">×</button>
                            </div>
                        </div>
                        
                        <button type="button" class="add-line-btn" id="add-line-btn">+ Add Line</button>
                        
                        <div class="form-group" id="totals-display">
                            <p>Debit Total: <span id="debit-total">0.00</span></p>
                            <p>Credit Total: <span id="credit-total">0.00</span></p>
                        </div>
                        
                        <div class="form-actions">
                            <button type="button" class="secondary" id="cancel-journal-btn">Cancel</button>
                            <button type="submit" class="primary">Save Entry</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        // Append form to the body
        const formContainer = document.createElement('div');
        formContainer.innerHTML = formHTML;
        document.body.appendChild(formContainer.firstElementChild);
        
        // Add event listeners
        document.getElementById('cancel-journal-btn').addEventListener('click', closeJournalForm);
        document.getElementById('journal-form').addEventListener('submit', saveJournalEntry);
        document.getElementById('add-line-btn').addEventListener('click', addJournalLine);
        
        // Set up line deletion handlers
        setupLineHandlers();
        
        // Set up debit/credit mutual exclusion
        setupDebitCreditFields();
        
        // Initial calculation
        calculateTotals();
        
    }).catch(error => {
        console.error('Error loading accounts:', error);
        alert('Failed to load accounts for journal entry form');
    });
}

function closeJournalForm() {
    const modal = document.getElementById('journal-form-modal');
    if (modal) {
        modal.remove();
    }
}

function addJournalLine() {
    // Get all accounts
    const accountOptions = document.querySelector('.account-select').innerHTML;
    
    const newLine = document.createElement('div');
    newLine.className = 'transaction-line';
    newLine.innerHTML = `
        <select class="account-select" required>
            ${accountOptions}
        </select>
        <input type="number" class="debit-amount" step="0.01" placeholder="Debit">
        <input type="number" class="credit-amount" step="0.01" placeholder="Credit">
        <button type="button" class="remove-line">×</button>
    `;
    
    document.getElementById('transaction-lines').appendChild(newLine);
    
    // Set up event handlers for the new line
    setupLineHandlers(newLine);
    setupDebitCreditFields(newLine);
}

function setupLineHandlers(line) {
    const container = line || document.getElementById('transaction-lines');
    
    const removeButtons = container.querySelectorAll('.remove-line');
    removeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // Don't remove if it's the last line
            const lines = document.querySelectorAll('.transaction-line');
            if (lines.length > 1) {
                this.closest('.transaction-line').remove();
                calculateTotals();
            }
        });
    });
}

function setupDebitCreditFields(line) {
    const container = line || document.getElementById('transaction-lines');
    
    const debitFields = container.querySelectorAll('.debit-amount');
    const creditFields = container.querySelectorAll('.credit-amount');
    
    debitFields.forEach(field => {
        field.addEventListener('input', function() {
            const creditField = this.closest('.transaction-line').querySelector('.credit-amount');
            if (this.value && parseFloat(this.value) > 0) {
                creditField.value = '';
                creditField.disabled = true;
            } else {
                creditField.disabled = false;
            }
            calculateTotals();
        });
    });
    
    creditFields.forEach(field => {
        field.addEventListener('input', function() {
            const debitField = this.closest('.transaction-line').querySelector('.debit-amount');
            if (this.value && parseFloat(this.value) > 0) {
                debitField.value = '';
                debitField.disabled = true;
            } else {
                debitField.disabled = false;
            }
            calculateTotals();
        });
    });
}

function calculateTotals() {
    let debitTotal = 0;
    let creditTotal = 0;
    
    // Calculate totals
    const lines = document.querySelectorAll('.transaction-line');
    lines.forEach(line => {
        const debitField = line.querySelector('.debit-amount');
        const creditField = line.querySelector('.credit-amount');
        
        if (debitField.value) {
            debitTotal += parseFloat(debitField.value) || 0;
        }
        
        if (creditField.value) {
            creditTotal += parseFloat(creditField.value) || 0;
        }
    });
    
    // Update display
    document.getElementById('debit-total').textContent = debitTotal.toFixed(2);
    document.getElementById('credit-total').textContent = creditTotal.toFixed(2);
    
    // Highlight imbalance
    const totalsDisplay = document.getElementById('totals-display');
    if (Math.abs(debitTotal - creditTotal) > 0.001) {
        totalsDisplay.classList.add('error');
    } else {
        totalsDisplay.classList.remove('error');
    }
}

async function saveJournalEntry(e) {
    e.preventDefault();
    
    // Check if debits = credits
    const debitTotal = parseFloat(document.getElementById('debit-total').textContent);
    const creditTotal = parseFloat(document.getElementById('credit-total').textContent);
    
    if (Math.abs(debitTotal - creditTotal) > 0.001) {
        alert('Journal entry must balance. Debits must equal credits.');
        return;
    }
    
    // Gather entry data
    const entryData = {
        date: document.getElementById('journal-date').value,
        reference: document.getElementById('journal-reference').value,
        description: document.getElementById('journal-description').value,
        lines: []
    };
    
    // Get all lines
    const lines = document.querySelectorAll('.transaction-line');
    lines.forEach(line => {
        const accountSelect = line.querySelector('.account-select');
        const debitField = line.querySelector('.debit-amount');
        const creditField = line.querySelector('.credit-amount');
        
        if (accountSelect.value) {
            // Determine if it's a debit or credit and set appropriate fields
            if (debitField.value && parseFloat(debitField.value) > 0) {
                const lineData = {
                    account_id: accountSelect.value,
                    amount: parseFloat(debitField.value),
                    type: 'debit'
                };
                entryData.lines.push(lineData);
            } else if (creditField.value && parseFloat(creditField.value) > 0) {
                const lineData = {
                    account_id: accountSelect.value,
                    amount: parseFloat(creditField.value),
                    type: 'credit'
                };
                entryData.lines.push(lineData);
            }
        }
    });
    
    // Validate - must have at least 2 lines
    if (entryData.lines.length < 2) {
        alert('A journal entry must have at least 2 lines.');
        return;
    }
    
    try {
        const result = await apiFetch('/ledger/journal/entries', {
            method: 'POST',
            body: entryData
        });
        
        if (result.ok) {
            closeJournalForm();
            loadJournalEntries();
        } else {
            alert(result.data && result.data.message ? result.data.message : 'Failed to save journal entry');
        }
    } catch (error) {
        console.error('Error saving journal entry:', error);
        alert('An error occurred while saving the journal entry');
    }
}

async function deleteJournalEntry(entryId) {
    if (!confirm('Are you sure you want to delete this journal entry? This action cannot be undone.')) {
        return;
    }
    
    try {
        const result = await apiFetch(`/ledger/journal/entries/${entryId}`, {
            method: 'DELETE'
        });
        
        if (result.ok) {
            loadJournalEntries();
        } else {
            alert(result.data && result.data.message ? result.data.message : 'Failed to delete journal entry');
        }
    } catch (error) {
        console.error('Error deleting journal entry:', error);
        alert('An error occurred while deleting the journal entry');
    }
}

// Export functions to make them accessible to other modules
window.Journal = {
    loadJournalEntries,
    renderJournalEntriesList,
    showNewJournalEntryForm,
    viewJournalEntry,
    deleteJournalEntry
};