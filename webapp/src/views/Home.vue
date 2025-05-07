<template>
  <div class="home">
    <h1>Welcome to GeoFinance</h1>
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
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      // Data properties can be added here
    }
  },
  mounted() {
    document.title = 'GeoFinance - Home'
  }
}
</script>

<style scoped>
.home {
  text-align: center;
  padding: 20px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.dashboard-card {
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
</style>