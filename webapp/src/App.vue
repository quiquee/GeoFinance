<template>
  <div id="app">
    <header v-if="isLoggedIn">
      <h1>GeoFinance</h1>
      <nav>
        <router-link to="/">Home</router-link> |
        <router-link to="/accounts">Accounts</router-link> |
        <router-link to="/journal">Journal</router-link> |
        <router-link to="/reports">Reports</router-link>
        <div class="user-menu">
          <span>{{ currentUser?.name || currentUser?.username }}</span>
          <button @click="logout" class="btn-logout">Logout</button>
        </div>
      </nav>
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

export default {
  name: 'App',
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

    onMounted(() => {
      checkAuthStatus();
    });

    return {
      isLoggedIn,
      currentUser,
      logout
    };
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

nav {
  padding: 20px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  padding: 10px;
}

nav a.router-link-exact-active {
  color: #42b983;
}

header, footer {
  padding: 20px;
}

main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  flex-grow: 1;
}

.user-menu {
  position: absolute;
  right: 0;
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
</style>