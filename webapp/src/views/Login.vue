<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>GeoFinance</h1>
        <p>Accounting Software</p>
      </div>

      <form @submit.prevent="login" class="login-form">
        <div class="form-group" :class="{ 'has-error': errors.username }">
          <label for="username">Username</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            placeholder="Enter your username"
            autocomplete="username"
            required
          />
          <div v-if="errors.username" class="error-message">{{ errors.username }}</div>
        </div>
        
        <div class="form-group" :class="{ 'has-error': errors.password }">
          <label for="password">Password</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            placeholder="Enter your password"
            autocomplete="current-password"
            required
          />
          <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
        </div>
        
        <div class="form-group remember-me">
          <input type="checkbox" id="remember" v-model="rememberMe" />
          <label for="remember">Remember me</label>
        </div>
        
        <div v-if="loginError" class="login-error">
          {{ loginError }}
        </div>
        
        <div class="form-actions">
          <button type="submit" class="btn-login" :disabled="isLoading">
            <span v-if="isLoading">Logging in...</span>
            <span v-else>Login</span>
          </button>
        </div>
      </form>

      <div class="login-footer">
        <p>Don't have an account? Contact your administrator.</p>
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
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  margin-bottom: 5px;
  color: #42b983;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-weight: 600;
  color: #333;
}

.form-group input[type="text"],
.form-group input[type="password"] {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #42b983;
}

.form-group.has-error input {
  border-color: #dc3545;
}

.error-message {
  color: #dc3545;
  font-size: 14px;
  margin-top: 5px;
}

.remember-me {
  flex-direction: row !important;
  align-items: center;
  gap: 10px;
}

.remember-me input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.form-actions {
  margin-top: 10px;
}

.btn-login {
  width: 100%;
  padding: 12px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-login:hover {
  background-color: #3aa876;
}

.btn-login:disabled {
  background-color: #a3d5c3;
  cursor: not-allowed;
}

.login-error {
  color: #dc3545;
  text-align: center;
  padding: 10px;
  background-color: rgba(220, 53, 69, 0.1);
  border-radius: 4px;
}

.login-footer {
  margin-top: 30px;
  text-align: center;
  color: #666;
  font-size: 14px;
}
</style>