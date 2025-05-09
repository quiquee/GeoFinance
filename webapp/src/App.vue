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
/* Import the CSS variables */
@import './styles/variables.css';

#app {
  font-family: var(--font-family-base);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--color-text);
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
  padding: var(--space-sm) var(--space-lg);
  background-color: var(--color-surface);
  box-shadow: var(--shadow-sm);
  height: var(--header-height);
}

.app-branding {
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.app-branding:hover {
  opacity: 0.8;
}

.app-branding h1 {
  margin: 0;
  font-size: var(--font-size-xl);
  color: var(--color-text);
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
  gap: var(--space-sm);
}

.btn-logout {
  background-color: var(--color-background-alt);
  border: none;
  padding: var(--space-xxs) var(--space-sm);
  border-radius: var(--button-radius);
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-text);
  transition: all var(--transition-fast);
}

.btn-logout:hover {
  background-color: var(--color-border);
}

footer {
  padding: var(--space-lg);
  text-align: center;
  background-color: var(--color-background-alt);
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .main-header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-xs);
  }
  
  .user-menu {
    margin-top: 0;
  }
}
</style>