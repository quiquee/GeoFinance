<template>
  <div class="dashboard-grid">
    <div class="dashboard-card">
      <h3>Account Summary</h3>
      <p>Quick view of your account balances</p>
      <router-link to="/accounts" class="btn">View Accounts</router-link>
    </div>
    <div class="dashboard-card">
      <h3>Recent Transactions</h3>
      <p>View your most recent journal entries</p>
      <router-link to="/journal" class="btn">Go to Journal</router-link>
    </div>
    <div class="dashboard-card">
      <h3>Financial Reports</h3>
      <p>Generate financial statements and analysis</p>
      <router-link to="/reports" class="btn">View Reports</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardCards'
}
</script>

<style scoped>
.dashboard-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  padding: 20px;
}

.dashboard-card {
  flex: 1 1 calc(33.333% - 40px);
  max-width: 300px;
  box-sizing: border-box;
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.dashboard-card:hover {
  transform: translateY(-5px);
}

.btn {
  display: inline-block;
  background-color: #42b983;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  margin-top: 15px;
  text-decoration: none;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #3aa876;
}

@media (max-width: 768px) {
  .dashboard-card {
    flex: 1 1 calc(50% - 20px);
  }
}

@media (max-width: 480px) {
  .dashboard-card {
    flex: 1 1 100%;
  }
}
</style>