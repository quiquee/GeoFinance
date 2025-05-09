<template>
  <div class="date-range-picker">
    <div class="date-inputs">
      <div class="date-field">
        <label :for="startDateId">{{ startLabel }}</label>
        <input 
          type="date" 
          :id="startDateId" 
          v-model="localStartDate"
          :min="minDate"
          :max="maxDate || localEndDate"
          class="date-input"
          :disabled="disabled"
        />
      </div>
      <div class="date-field">
        <label :for="endDateId">{{ endLabel }}</label>
        <input 
          type="date" 
          :id="endDateId" 
          v-model="localEndDate"
          :min="localStartDate || minDate"
          :max="maxDate"
          class="date-input"
          :disabled="disabled"
        />
      </div>
    </div>
    <div class="date-presets" v-if="showPresets">
      <button 
        v-for="preset in availablePresets" 
        :key="preset.key"
        @click="applyPreset(preset.key)"
        class="preset-button"
        :class="{ active: activePreset === preset.key }"
        :disabled="disabled"
      >
        {{ preset.label }}
      </button>
    </div>
    <div class="apply-button" v-if="showApplyButton">
      <button @click="applyDates" class="btn-apply" :disabled="!isValid || disabled">{{ applyButtonText }}</button>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue';

export default {
  name: 'DateRangePicker',
  props: {
    startDate: {
      type: String,
      default: ''
    },
    endDate: {
      type: String,
      default: ''
    },
    startLabel: {
      type: String,
      default: 'Start Date:'
    },
    endLabel: {
      type: String,
      default: 'End Date:'
    },
    minDate: {
      type: String,
      default: ''
    },
    maxDate: {
      type: String,
      default: ''
    },
    showPresets: {
      type: Boolean,
      default: true
    },
    showApplyButton: {
      type: Boolean,
      default: true
    },
    applyButtonText: {
      type: String,
      default: 'Apply'
    },
    disabled: {
      type: Boolean,
      default: false
    },
    presets: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:startDate', 'update:endDate', 'apply'],
  setup(props, { emit }) {
    const localStartDate = ref(props.startDate);
    const localEndDate = ref(props.endDate);
    const activePreset = ref(null);
    const startDateId = `start-date-${Math.random().toString(36).substr(2, 9)}`;
    const endDateId = `end-date-${Math.random().toString(36).substr(2, 9)}`;

    const defaultPresets = [
      { key: 'today', label: 'Today' },
      { key: 'yesterday', label: 'Yesterday' },
      { key: 'this-week', label: 'This Week' },
      { key: 'last-week', label: 'Last Week' },
      { key: 'this-month', label: 'This Month' },
      { key: 'last-month', label: 'Last Month' },
      { key: 'this-year', label: 'This Year' },
    ];

    const availablePresets = computed(() => {
      return props.presets.length > 0 ? props.presets : defaultPresets;
    });

    const isValid = computed(() => {
      return localStartDate.value && localEndDate.value;
    });

    const formatDateForInput = (date) => {
      // Format date in local YYYY-MM-DD to avoid UTC offset issues without using UTC methods
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    };

    const applyPreset = (presetKey) => {
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);

      let start, end;

      switch (presetKey) {
        case 'today':
          start = end = formatDateForInput(today);
          break;
        case 'yesterday':
          start = end = formatDateForInput(yesterday);
          break;
        case 'this-week':
          start = formatDateForInput(new Date(today.setDate(today.getDate() - today.getDay())));
          end = formatDateForInput(new Date());
          break;
        case 'last-week':
          const lastSunday = new Date(today);
          lastSunday.setDate(today.getDate() - today.getDay() - 7);
          const lastSaturday = new Date(lastSunday);
          lastSaturday.setDate(lastSunday.getDate() + 6);
          start = formatDateForInput(lastSunday);
          end = formatDateForInput(lastSaturday);
          break;
        case 'this-month':
          start = formatDateForInput(new Date(now.getFullYear(), now.getMonth(), 1));
          end = formatDateForInput(new Date());
          break;
        case 'last-month':
          start = formatDateForInput(new Date(now.getFullYear(), now.getMonth() - 1, 1));
          end = formatDateForInput(new Date(now.getFullYear(), now.getMonth(), 0));
          break;
        case 'this-year':
          start = formatDateForInput(new Date(now.getFullYear(), 0, 1));
          end = formatDateForInput(new Date());
          break;
        default:
          // Custom preset handler for user-defined presets
          const customPreset = availablePresets.value.find(p => p.key === presetKey);
          if (customPreset && typeof customPreset.handler === 'function') {
            const result = customPreset.handler();
            start = result.start;
            end = result.end;
          }
          break;
      }

      if (start && end) {
        localStartDate.value = start;
        localEndDate.value = end;
        activePreset.value = presetKey;
        
        if (!props.showApplyButton) {
          applyDates();
        }
      }
    };

    const applyDates = () => {
      if (isValid.value) {
        emit('update:startDate', localStartDate.value);
        emit('update:endDate', localEndDate.value);
        emit('apply', { startDate: localStartDate.value, endDate: localEndDate.value });
      }
    };

    watch(() => props.startDate, (newVal) => {
      localStartDate.value = newVal;
    });

    watch(() => props.endDate, (newVal) => {
      localEndDate.value = newVal;
    });

    watch([localStartDate, localEndDate], () => {
      // Reset active preset when dates are changed manually
      if (activePreset.value) {
        activePreset.value = null;
      }
      
      // If no apply button, update values on change
      if (!props.showApplyButton && localStartDate.value && localEndDate.value) {
        emit('update:startDate', localStartDate.value);
        emit('update:endDate', localEndDate.value);
      }
    });

    onMounted(() => {
      // Set default dates if none provided
      if (!localStartDate.value && !localEndDate.value && !props.disabled) {
        applyPreset('this-month');
      }
    });

    return {
      localStartDate,
      localEndDate,
      startDateId,
      endDateId,
      isValid,
      availablePresets,
      activePreset,
      applyPreset,
      applyDates
    };
  }
};
</script>

<style scoped>
.date-range-picker {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 15px;
}

.date-inputs {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.date-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
  min-width: 180px;
}

.date-field label {
  font-weight: 500;
  color: #555;
}

.date-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 100%;
}

.date-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 5px;
}

.preset-button {
  padding: 5px 10px;
  border: 1px solid #ddd;
  background-color: #f8f9fa;
  border-radius: 15px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.preset-button:hover:not([disabled]) {
  background-color: #e9ecef;
  border-color: #ccc;
}

.preset-button.active {
  background-color: #42b983;
  border-color: #42b983;
  color: white;
}

.preset-button[disabled] {
  opacity: 0.5;
  cursor: not-allowed;
}

.apply-button {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.btn-apply {
  padding: 8px 16px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-apply:hover:not([disabled]) {
  background-color: #3aa876;
}

.btn-apply[disabled] {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>