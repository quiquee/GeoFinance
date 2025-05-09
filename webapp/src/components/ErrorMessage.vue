<template>
  <div class="error-message" :class="{ dismissible: allowDismiss }">
    <div class="error-icon" v-if="showIcon">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
    </div>
    <div class="error-content">
      <h4 v-if="title" class="error-title">{{ title }}</h4>
      <p class="error-text">{{ message }}</p>
      <div v-if="retry" class="error-actions">
        <button @click="$emit('retry')" class="btn-retry">{{ retryText }}</button>
      </div>
    </div>
    <button v-if="allowDismiss" @click="$emit('dismiss')" class="dismiss-button">×</button>
  </div>
</template>

<script>
export default {
  name: 'ErrorMessage',
  props: {
    title: {
      type: String,
      default: ''
    },
    message: {
      type: String,
      required: true
    },
    retry: {
      type: Boolean,
      default: false
    },
    retryText: {
      type: String,
      default: 'Retry'
    },
    allowDismiss: {
      type: Boolean,
      default: false
    },
    showIcon: {
      type: Boolean,
      default: true
    }
  },
  emits: ['retry', 'dismiss']
}
</script>

<style scoped>
.error-message {
  display: flex;
  padding: var(--space-md);
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: var(--radius-sm);
  margin: var(--space-md) 0;
  align-items: flex-start;
}

.error-icon {
  flex-shrink: 0;
  margin-right: var(--space-sm);
  color: var(--color-danger);
}

.error-content {
  flex-grow: 1;
}

.error-title {
  margin: 0 0 var(--space-xxs) 0;
  font-size: var(--font-size-md);
}

.error-text {
  margin: 0;
  line-height: var(--line-height-normal);
}

.error-actions {
  margin-top: var(--space-sm);
}

.btn-retry {
  background-color: var(--color-danger);
  color: var(--color-text-inverse);
  border: none;
  padding: var(--space-xxs) var(--space-sm);
  border-radius: var(--button-radius);
  cursor: pointer;
  font-size: var(--font-size-sm);
  transition: background-color var(--transition-fast);
}

.btn-retry:hover {
  background-color: #c82333;
}

.dismissible {
  position: relative;
  padding-right: 35px;
}

.dismiss-button {
  position: absolute;
  top: var(--space-sm);
  right: var(--space-sm);
  background: none;
  border: none;
  font-size: var(--font-size-lg);
  color: #721c24;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}
</style>