<template>
  <div :class="['loading-indicator', size]">
    <div class="spinner"></div>
    <p v-if="message" class="loading-message">{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: 'LoadingIndicator',
  props: {
    message: {
      type: String,
      default: 'Loading...'
    },
    size: {
      type: String,
      default: 'medium', // small, medium, large
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    }
  }
}
</script>

<style scoped>
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-lg);
  text-align: center;
}

.spinner {
  border: 3px solid var(--color-border-light);
  border-radius: 50%;
  border-top: 3px solid var(--color-primary);
  animation: spin 1s linear infinite;
}

.loading-message {
  margin-top: var(--space-sm);
  color: var(--color-text-secondary);
}

.small .spinner {
  width: 20px;
  height: 20px;
}

.medium .spinner {
  width: 30px;
  height: 30px;
}

.large .spinner {
  width: 50px;
  height: 50px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>