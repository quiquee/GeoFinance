<template>
  <div v-if="show" class="confirm-dialog-overlay" @click.self="cancel">
    <div class="confirm-dialog">
      <div class="confirm-dialog-header">
        <h3>{{ title }}</h3>
      </div>
      <div class="confirm-dialog-body">
        {{ message }}
      </div>
      <div class="confirm-dialog-footer">
        <button @click="cancel" class="btn-cancel">{{ cancelText }}</button>
        <button @click="confirm" class="btn-confirm" :class="{ 'btn-danger': danger }">{{ confirmText }}</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfirmDialog',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: 'Confirm'
    },
    message: {
      type: String,
      required: true
    },
    confirmText: {
      type: String,
      default: 'Confirm'
    },
    cancelText: {
      type: String,
      default: 'Cancel'
    },
    danger: {
      type: Boolean,
      default: false
    }
  },
  emits: ['cancel', 'confirm'],
  methods: {
    confirm() {
      this.$emit('confirm');
    },
    cancel() {
      this.$emit('cancel');
    }
  }
}
</script>

<style scoped>
.confirm-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: var(--z-index-modal);
}

.confirm-dialog {
  background-color: var(--color-surface);
  border-radius: var(--radius-md);
  width: 400px;
  max-width: 90%;
  box-shadow: var(--shadow-md);
  animation: dialog-fade-in var(--transition-fast);
}

.confirm-dialog-header {
  padding: var(--space-md) var(--space-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.confirm-dialog-header h3 {
  margin: 0;
  font-size: var(--font-size-md);
  color: var(--color-text);
}

.confirm-dialog-body {
  padding: var(--space-lg);
  line-height: var(--line-height-normal);
}

.confirm-dialog-footer {
  padding: var(--space-md) var(--space-lg);
  border-top: 1px solid var(--color-border-light);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
}

.btn-cancel, .btn-confirm {
  padding: var(--space-xs) var(--space-md);
  border: none;
  border-radius: var(--button-radius);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.btn-cancel {
  background-color: var(--color-background-alt);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-cancel:hover {
  background-color: var(--color-border-light);
}

.btn-confirm {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn-confirm:hover {
  background-color: var(--color-primary-dark);
}

.btn-confirm.btn-danger {
  background-color: var(--color-danger);
}

.btn-confirm.btn-danger:hover {
  background-color: #c82333;
}

@keyframes dialog-fade-in {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>