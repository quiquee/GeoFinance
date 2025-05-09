<template>
  <div v-if="show" class="modal-overlay" @click.self="cancel">
    <div class="modal-content" :style="{ width: width }">
      <div class="modal-header">
        <h2>{{ title }}</h2>
        <button v-if="showCloseButton" @click="cancel" class="modal-close-btn">&times;</button>
      </div>
      
      <div class="modal-body">
        <slot></slot>
      </div>
      
      <div v-if="$slots.footer" class="modal-footer">
        <slot name="footer"></slot>
      </div>
      <div v-else-if="showDefaultFooter" class="modal-footer">
        <button @click="cancel" class="btn-secondary">{{ cancelText }}</button>
        <button @click="confirm" class="btn-primary">{{ confirmText }}</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ModalForm',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      default: 'Modal'
    },
    width: {
      type: String,
      default: '500px'
    },
    confirmText: {
      type: String,
      default: 'Save'
    },
    cancelText: {
      type: String,
      default: 'Cancel'
    },
    showCloseButton: {
      type: Boolean,
      default: true
    },
    showDefaultFooter: {
      type: Boolean,
      default: true
    }
  },
  emits: ['update:show', 'confirm', 'cancel'],
  methods: {
    confirm() {
      this.$emit('confirm');
    },
    cancel() {
      this.$emit('cancel');
      this.$emit('update:show', false);
    }
  }
}
</script>

<style scoped>
.modal-overlay {
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

.modal-content {
  background-color: var(--color-surface);
  border-radius: var(--radius-md);
  max-width: 90%;
  box-shadow: var(--shadow-md);
  animation: modal-fade-in var(--transition-fast);
}

.modal-header {
  padding: var(--space-md) var(--space-lg);
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: var(--font-size-md);
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: var(--font-size-xl);
  cursor: pointer;
  color: var(--color-text-tertiary);
}

.modal-body {
  padding: var(--space-lg);
}

.modal-footer {
  padding: var(--space-md) var(--space-lg);
  border-top: 1px solid var(--color-border-light);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
}

.btn-primary {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border: none;
  padding: var(--space-xs) var(--space-md);
  border-radius: var(--button-radius);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
}

.btn-secondary {
  background-color: var(--color-secondary);
  color: var(--color-text-inverse);
  border: none;
  padding: var(--space-xs) var(--space-md);
  border-radius: var(--button-radius);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.btn-secondary:hover {
  background-color: var(--color-secondary-dark);
}

@keyframes modal-fade-in {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>