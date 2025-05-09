<template>
  <div class="home">
    <div v-if="loading" class="loading">
      <p>Loading dashboard...</p>
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    
    <DashboardCards v-if="!loading && !error" />
  </div>
</template>

<script>
import DashboardCards from '../components/DashboardCards.vue';

export default {
  name: 'HomeView',
  components: {
    DashboardCards
  },
  data() {
    return {
      loading: false,
      error: null
    }
  },
  mounted() {
    document.title = 'GeoFinance - Home';
  }
}
</script>

<style scoped>
.home {
  padding: 0;
  text-align: center;
}

.loading, .error {
  padding: 20px;
  color: #666;
}

.error {
  color: #dc3545;
}
</style>