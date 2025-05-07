// Overview section functionality
async function loadOverviewData() {
    try {
        // Load account balances
        const balanceResult = await apiFetch('/ledger/balance');
        if (balanceResult.ok && balanceResult.data) {
            renderAccountBalances(balanceResult.data);
        } else {
            document.getElementById('balance-panel').innerHTML = '<h3>Account Balances</h3><p>Failed to load balances</p>';
        }
        
        // Load recent journal entries
        const entriesResult = await apiFetch('/ledger/journal/entries');
        if (entriesResult.ok && entriesResult.data) {
            renderRecentEntries(entriesResult.data.slice(0, 5)); // Show only 5 most recent
        } else {
            document.getElementById('recent-entries-panel').innerHTML = '<h3>Recent Journal Entries</h3><p>Failed to load entries</p>';
        }
    } catch (error) {
        console.error('Error loading overview data:', error);
    }
}

function renderAccountBalances(balances) {
    const panel = document.getElementById('balance-panel');
    if (!balances || balances.length === 0) {
        panel.innerHTML = '<h3>Account Balances</h3><p>No accounts found</p>';
        return;
    }
    
    let html = '<h3>Account Balances</h3><table class="data-table"><thead><tr><th>Account</th><th>Balance</th></tr></thead><tbody>';
    
    balances.forEach(account => {
        html += `<tr>
            <td>${account.account_number} - ${account.account_name}</td>
            <td class="amount">${parseFloat(account.balance).toFixed(2)}</td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    panel.innerHTML = html;
}

function renderRecentEntries(entries) {
    const panel = document.getElementById('recent-entries-panel');
    if (!entries || entries.length === 0) {
        panel.innerHTML = '<h3>Recent Journal Entries</h3><p>No entries found</p>';
        return;
    }
    
    let html = '<h3>Recent Journal Entries</h3><table class="data-table"><thead><tr><th>Date</th><th>Description</th></tr></thead><tbody>';
    
    entries.forEach(entry => {
        const date = new Date(entry.date).toLocaleDateString();
        html += `<tr>
            <td>${date}</td>
            <td>${entry.description}</td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    panel.innerHTML = html;
}

// Export functions to make them accessible to other modules
window.Overview = {
    loadOverviewData,
    renderAccountBalances,
    renderRecentEntries
};