// Accounts section functionality
async function loadAccountsData() {
    try {
        // Load all accounts
        const result = await apiFetch('/ledger/accounts');
        if (result.ok && result.data) {
            renderAccountsList(result.data);
        } else {
            document.getElementById('accounts-list').innerHTML = '<p>Failed to load accounts</p>';
        }
    } catch (error) {
        console.error('Error loading accounts data:', error);
        document.getElementById('accounts-list').innerHTML = '<p>Error loading accounts</p>';
    }
}

function renderAccountsList(accounts) {
    const accountsList = document.getElementById('accounts-list');
    if (!accounts || accounts.length === 0) {
        accountsList.innerHTML = '<p>No accounts found</p>';
        return;
    }
    
    let html = '<table class="data-table"><thead><tr>' +
        '<th>Account #</th>' +
        '<th>Name</th>' +
        '<th>Type</th>' +
        '<th>Actions</th>' +
        '</tr></thead><tbody>';
    
    accounts.forEach(account => {
        // Use the correct property names from the API response
        html += `<tr>
            <td>${account.number}</td>
            <td>${account.name}</td>
            <td>${account.type}</td>
            <td>
                <button class="edit-account-btn" data-id="${account.id}">Edit</button>
                <button class="delete-account-btn" data-id="${account.id}">Delete</button>
            </td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    accountsList.innerHTML = html;
    
    // Add event listeners for edit and delete buttons
    document.querySelectorAll('.edit-account-btn').forEach(btn => {
        btn.addEventListener('click', () => editAccount(btn.getAttribute('data-id')));
    });
    
    document.querySelectorAll('.delete-account-btn').forEach(btn => {
        btn.addEventListener('click', () => deleteAccount(btn.getAttribute('data-id')));
    });
}

function showNewAccountForm() {
    const formHTML = `
        <div class="form-modal active" id="account-form-modal">
            <div class="modal-content">
                <h3>New Account</h3>
                <form id="account-form">
                    <div class="form-group">
                        <label for="account-number">Account Number</label>
                        <input type="text" id="account-number" required>
                    </div>
                    <div class="form-group">
                        <label for="account-name">Account Name</label>
                        <input type="text" id="account-name" required>
                    </div>
                    <div class="form-group">
                        <label for="account-type">Account Type</label>
                        <select id="account-type" required>
                            <option value="asset">Asset</option>
                            <option value="liability">Liability</option>
                            <option value="equity">Equity</option>
                            <option value="income">Income</option>
                            <option value="expense">Expense</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="account-description">Description</label>
                        <input type="text" id="account-description">
                    </div>
                    <div class="form-group">
                        <label for="account-initial-balance">Initial Balance</label>
                        <input type="number" id="account-initial-balance" step="0.01" value="0.00">
                    </div>
                    <div class="form-actions">
                        <button type="button" class="secondary" id="cancel-account-btn">Cancel</button>
                        <button type="submit" class="primary">Save Account</button>
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
    document.getElementById('cancel-account-btn').addEventListener('click', closeAccountForm);
    document.getElementById('account-form').addEventListener('submit', saveAccount);
}

function closeAccountForm() {
    const modal = document.getElementById('account-form-modal');
    if (modal) {
        modal.remove();
    }
}

async function saveAccount(e) {
    e.preventDefault();
    
    const accountData = {
        // Update property names to match the expected API request format
        number: document.getElementById('account-number').value,
        name: document.getElementById('account-name').value,
        type: document.getElementById('account-type').value,
        description: document.getElementById('account-description').value,
        initial_balance: parseFloat(document.getElementById('account-initial-balance').value) || 0
    };
    
    try {
        const result = await apiFetch('/ledger/accounts', {
            method: 'POST',
            body: accountData
        });
        
        if (result.ok) {
            closeAccountForm();
            loadAccountsData();
        } else {
            alert(result.data && result.data.message ? result.data.message : 'Failed to save account');
        }
    } catch (error) {
        console.error('Error saving account:', error);
        alert('An error occurred while saving the account');
    }
}

async function editAccount(accountId) {
    try {
        const result = await apiFetch(`/ledger/accounts/${accountId}`);
        if (!result.ok || !result.data) {
            alert('Failed to load account details');
            return;
        }
        
        const account = result.data;
        
        const formHTML = `
            <div class="form-modal active" id="account-form-modal">
                <div class="modal-content">
                    <h3>Edit Account</h3>
                    <form id="account-form">
                        <input type="hidden" id="account-id" value="${account.id}">
                        <div class="form-group">
                            <label for="account-number">Account Number</label>
                            <input type="text" id="account-number" value="${account.number}" required>
                        </div>
                        <div class="form-group">
                            <label for="account-name">Account Name</label>
                            <input type="text" id="account-name" value="${account.name}" required>
                        </div>
                        <div class="form-group">
                            <label for="account-type">Account Type</label>
                            <select id="account-type" required>
                                <option value="asset" ${account.type === 'asset' ? 'selected' : ''}>Asset</option>
                                <option value="liability" ${account.type === 'liability' ? 'selected' : ''}>Liability</option>
                                <option value="equity" ${account.type === 'equity' ? 'selected' : ''}>Equity</option>
                                <option value="income" ${account.type === 'income' ? 'selected' : ''}>Income</option>
                                <option value="expense" ${account.type === 'expense' ? 'selected' : ''}>Expense</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="account-description">Description</label>
                            <input type="text" id="account-description" value="${account.description || ''}">
                        </div>
                        <div class="form-actions">
                            <button type="button" class="secondary" id="cancel-account-btn">Cancel</button>
                            <button type="submit" class="primary">Update Account</button>
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
        document.getElementById('cancel-account-btn').addEventListener('click', closeAccountForm);
        document.getElementById('account-form').addEventListener('submit', updateAccount);
        
    } catch (error) {
        console.error('Error loading account details:', error);
        alert('An error occurred while loading account details');
    }
}

async function updateAccount(e) {
    e.preventDefault();
    
    const accountId = document.getElementById('account-id').value;
    const accountData = {
        // Update property names to match the expected API request format
        number: document.getElementById('account-number').value,
        name: document.getElementById('account-name').value,
        type: document.getElementById('account-type').value,
        description: document.getElementById('account-description').value,
    };
    
    try {
        const result = await apiFetch(`/ledger/accounts/${accountId}`, {
            method: 'PUT',
            body: accountData
        });
        
        if (result.ok) {
            closeAccountForm();
            loadAccountsData();
        } else {
            alert(result.data && result.data.message ? result.data.message : 'Failed to update account');
        }
    } catch (error) {
        console.error('Error updating account:', error);
        alert('An error occurred while updating the account');
    }
}

async function deleteAccount(accountId) {
    if (!confirm('Are you sure you want to delete this account? This action cannot be undone.')) {
        return;
    }
    
    try {
        const result = await apiFetch(`/ledger/accounts/${accountId}`, {
            method: 'DELETE'
        });
        
        if (result.ok) {
            loadAccountsData();
        } else {
            alert(result.data && result.data.message ? result.data.message : 'Failed to delete account');
        }
    } catch (error) {
        console.error('Error deleting account:', error);
        alert('An error occurred while deleting the account');
    }
}

// Export functions to make them accessible to other modules
window.Accounts = {
    loadAccountsData,
    renderAccountsList,
    showNewAccountForm,
    editAccount,
    deleteAccount
};