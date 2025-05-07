// Reports section functionality

async function loadReport(reportType) {
    const reportContainer = document.getElementById('report-container');
    reportContainer.innerHTML = '<div class="loading">Loading report...</div>';
    
    try {
        const result = await apiFetch(`/ledger/${reportType}`);
        if (result.ok && result.data) {
            // Different rendering based on report type
            switch (reportType) {
                case 'trial-balance':
                    renderTrialBalanceReport(result.data);
                    break;
                case 'income-statement':
                    renderIncomeStatementReport(result.data);
                    break;
                case 'balance-sheet':
                    renderBalanceSheetReport(result.data);
                    break;
                default:
                    reportContainer.innerHTML = '<p>Unknown report type</p>';
            }
        } else {
            reportContainer.innerHTML = '<p>Failed to load report</p>';
        }
    } catch (error) {
        console.error(`Error loading ${reportType}:`, error);
        reportContainer.innerHTML = '<p>Error occurred while loading report</p>';
    }
}

function renderTrialBalanceReport(data) {
    // Implementation for trial balance report rendering
    const reportContainer = document.getElementById('report-container');
    
    let html = `
        <h3>Trial Balance</h3>
        <table class="report-table">
            <thead>
                <tr>
                    <th>Account</th>
                    <th>Debit</th>
                    <th>Credit</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.trial_balance.forEach(item => {
        html += `
            <tr>
                <td>${item.account_number} - ${item.account_name}</td>
                <td class="amount">${parseFloat(item.debit_balance).toFixed(2)}</td>
                <td class="amount">${parseFloat(item.credit_balance).toFixed(2)}</td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
            <tfoot>
                <tr>
                    <th>Total</th>
                    <th class="amount">${parseFloat(data.total_debits).toFixed(2)}</th>
                    <th class="amount">${parseFloat(data.total_credits).toFixed(2)}</th>
                </tr>
            </tfoot>
        </table>
    `;
    
    reportContainer.innerHTML = html;
}

function renderIncomeStatementReport(data) {
    // Implementation for income statement rendering
    const reportContainer = document.getElementById('report-container');
    
    let html = '<h3>Income Statement</h3>';
    
    // Income section
    html += '<h4>Income</h4><table class="report-table"><tbody>';
    if (data.income_accounts.length === 0) {
        html += '<tr><td colspan="2">No income accounts</td></tr>';
    } else {
        data.income_accounts.forEach(account => {
            html += `<tr>
                <td>${account.account_name}</td>
                <td class="amount">${parseFloat(account.balance).toFixed(2)}</td>
            </tr>`;
        });
    }
    html += `<tr class="subtotal">
        <td>Total Income</td>
        <td class="amount">${parseFloat(data.total_income).toFixed(2)}</td>
    </tr></tbody></table>`;
    
    // Expenses section
    html += '<h4>Expenses</h4><table class="report-table"><tbody>';
    if (data.expense_accounts.length === 0) {
        html += '<tr><td colspan="2">No expense accounts</td></tr>';
    } else {
        data.expense_accounts.forEach(account => {
            html += `<tr>
                <td>${account.account_name}</td>
                <td class="amount">${parseFloat(account.balance).toFixed(2)}</td>
            </tr>`;
        });
    }
    html += `<tr class="subtotal">
        <td>Total Expenses</td>
        <td class="amount">${parseFloat(data.total_expenses).toFixed(2)}</td>
    </tr></tbody></table>`;
    
    // Net Income
    html += `<div class="net-result">
        <strong>Net Income</strong>
        <span class="amount">${parseFloat(data.net_income).toFixed(2)}</span>
    </div>`;
    
    reportContainer.innerHTML = html;
}

function renderBalanceSheetReport(data) {
    // Implementation for balance sheet rendering
    const reportContainer = document.getElementById('report-container');
    
    let html = '<h3>Balance Sheet</h3>';
    
    // Assets section
    html += '<h4>Assets</h4><table class="report-table"><tbody>';
    if (data.asset_accounts.length === 0) {
        html += '<tr><td colspan="2">No asset accounts</td></tr>';
    } else {
        data.asset_accounts.forEach(account => {
            html += `<tr>
                <td>${account.account_name}</td>
                <td class="amount">${parseFloat(account.balance).toFixed(2)}</td>
            </tr>`;
        });
    }
    html += `<tr class="subtotal">
        <td>Total Assets</td>
        <td class="amount">${parseFloat(data.total_assets).toFixed(2)}</td>
    </tr></tbody></table>`;
    
    // Liabilities section
    html += '<h4>Liabilities</h4><table class="report-table"><tbody>';
    if (data.liability_accounts.length === 0) {
        html += '<tr><td colspan="2">No liability accounts</td></tr>';
    } else {
        data.liability_accounts.forEach(account => {
            html += `<tr>
                <td>${account.account_name}</td>
                <td class="amount">${parseFloat(account.balance).toFixed(2)}</td>
            </tr>`;
        });
    }
    html += `<tr class="subtotal">
        <td>Total Liabilities</td>
        <td class="amount">${parseFloat(data.total_liabilities).toFixed(2)}</td>
    </tr></tbody></table>`;
    
    // Equity section
    html += '<h4>Equity</h4><table class="report-table"><tbody>';
    if (data.equity_accounts.length === 0) {
        html += '<tr><td colspan="2">No equity accounts</td></tr>';
    } else {
        data.equity_accounts.forEach(account => {
            html += `<tr>
                <td>${account.account_name}</td>
                <td class="amount">${parseFloat(account.balance).toFixed(2)}</td>
            </tr>`;
        });
    }
    html += `<tr class="subtotal">
        <td>Total Equity</td>
        <td class="amount">${parseFloat(data.total_equity).toFixed(2)}</td>
    </tr></tbody></table>`;
    
    reportContainer.innerHTML = html;
}

// Export functions to make them accessible to other modules
window.Reports = {
    loadReport,
    renderTrialBalanceReport,
    renderIncomeStatementReport,
    renderBalanceSheetReport
};