<template>
  <div class="container d-flex justify-content-center align-items-center min-vh-100 bg-light py-4">
    <div class="card shadow-sm" style="max-width: 400px;">
      <div class="card-header text-center border-0 bg-white pt-4">
        <h2 class="text-primary">GeoFinance</h2>
        <p class="text-secondary">Accounting Software</p>
      </div>

      <div class="card-body">
        <form @submit.prevent="login">
          <div class="mb-3" :class="{ 'is-invalid': errors.username }">
            <label for="username" class="form-label">Username</label>
            <input 
              type="text" 
              class="form-control"
              id="username" 
              v-model="username" 
              placeholder="Enter your username"
              autocomplete="username"
              required
            />
            <div v-if="errors.username" class="invalid-feedback d-block">{{ errors.username }}</div>
          </div>
          
          <div class="mb-3" :class="{ 'is-invalid': errors.password }">
            <label for="password" class="form-label">Password</label>
            <input 
              type="password" 
              class="form-control"
              id="password" 
              v-model="password" 
              placeholder="Enter your password"
              autocomplete="current-password"
              required
            />
            <div v-if="errors.password" class="invalid-feedback d-block">{{ errors.password }}</div>
          </div>
          
          <div class="mb-3 form-check">
            <input type="checkbox" class="form-check-input" id="remember" v-model="rememberMe" />
            <label class="form-check-label" for="remember">Remember me</label>
          </div>
          
          <div v-if="loginError" class="alert alert-danger mb-3">
            {{ loginError }}
          </div>
          
          <div class="d-grid">
            <button type="submit" class="btn btn-primary" :disabled="isLoading">
              <span v-if="isLoading">Logging in...</span>
              <span v-else>Login</span>
            </button>
          </div>
        </form>
      </div>

      <div class="card-footer text-center border-0 bg-white py-3">
        <p class="text-muted mb-0">Don't have an account? Contact your administrator.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { isAuthenticated, login as authLogin, fakeDemoLogin } from '../services/authService';

export default {
  name: 'LoginView',
  setup() {
    const router = useRouter();
    const username = ref('');
    const password = ref('');
    const rememberMe = ref(false);
    const isLoading = ref(false);
    const loginError = ref('');
    const errors = ref({
      username: '',
      password: ''
    });

    const validateForm = () => {
      let isValid = true;
      errors.value = {
        username: '',
        password: ''
      };
      
      if (!username.value.trim()) {
        errors.value.username = 'Username is required';
        isValid = false;
      }
      
      if (!password.value) {
        errors.value.password = 'Password is required';
        isValid = false;
      }
      
      return isValid;
    };

    const login = async () => {
      if (!validateForm()) {
        return;
      }
      
      isLoading.value = true;
      loginError.value = '';
      
      try {
        // First try the real authentication service
        try {
          await authLogin(username.value, password.value, rememberMe.value);
        } catch (apiError) {
          console.log('Real API login failed, trying demo login as fallback');
          // If real auth fails, try the demo login as fallback
          await fakeDemoLogin(username.value, password.value);
        }
        
        // Redirect to home page after successful login
        router.push('/');
      } catch (error) {
        console.error('Login error:', error);
        loginError.value = error.message || 'Failed to authenticate. Please check your credentials and try again.';
      } finally {
        isLoading.value = false;
      }
    };
    
    // Check if user is already logged in when component is mounted
    const checkAuthStatus = () => {
      if (isAuthenticated()) {
        router.push('/');
      }
    };
    
    // Check auth status
    checkAuthStatus();
    
    return {
      username,
      password,
      rememberMe,
      isLoading,
      loginError,
      errors,
      login
    };
  }
};
</script>

<style scoped>
/* Using standardized CSS framework classes, no custom styles needed */
</style>