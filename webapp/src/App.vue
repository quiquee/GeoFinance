<template>
  <div id="app">
    <header v-if="isLoggedIn" class="main-header">
      <div class="app-branding" @click="goToHome">
        <h1>GeoFinance</h1>
      </div>
      
      <FinancialBanner v-if="isLoggedIn" />
      <div class="user-menu">
        <span>{{ currentUser?.name || currentUser?.username }}</span>
        <button @click="logout" class="btn-logout">Logout</button>
      </div>
    </header>
    <main>
      <router-view/>
    </main>
    <footer v-if="isLoggedIn">
      <p>© 2025 GeoFinance - Accounting Software</p>
    </footer>
  </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { isAuthenticated, getCurrentUser, logout as authLogout } from './services/authService';
import FinancialBanner from './components/FinancialBanner.vue';

export default {
  name: 'App',
  components: {
    FinancialBanner
  },
  setup() {
    const router = useRouter();
    const isLoggedIn = ref(false);
    const currentUser = ref(null);

    const checkAuthStatus = () => {
      isLoggedIn.value = isAuthenticated();
      if (isLoggedIn.value) {
        currentUser.value = getCurrentUser();
      }
    };

    const logout = () => {
      authLogout();
      isLoggedIn.value = false;
      currentUser.value = null;
      router.push('/login');
    };

    const goToHome = () => {
      router.push('/');
    };

    onMounted(() => {
      checkAuthStatus();
    });

    return {
      isLoggedIn,
      currentUser,
      logout,
      goToHome
    };
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
}

.main-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background-color: #ffffff;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.app-branding {
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.app-branding:hover {
  opacity: 0.8;
}

.app-branding h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #34495e;
}

main {
  max-width: 100%;
  margin: 0 auto;
  padding: 0;
  flex-grow: 1;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-logout {
  background-color: #f0f0f0;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: all 0.3s;
}

.btn-logout:hover {
  background-color: #e0e0e0;
}

footer {
  padding: 20px;
  text-align: center;
  background-color: #f8f9fa;
}

@media (max-width: 768px) {
  .main-header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 10px;
  }
  
  .user-menu {
    margin-top: 0;
  }
}
</style>