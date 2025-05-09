<template>
  <div class="base-table-wrapper">
    <table class="base-table">
      <thead>
        <tr>
          <th v-for="column in columns" :key="column.key" :class="column.headerClass">
            {{ column.label }}
          </th>
          <th v-if="hasActions" class="actions-column">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in items" :key="index">
          <td v-for="column in columns" :key="`${index}-${column.key}`" :class="column.cellClass">
            <slot :name="`cell-${column.key}`" :item="item" :value="item[column.key]">
              {{ formatValue(item[column.key], column.format) }}
            </slot>
          </td>
          <td v-if="hasActions" class="actions-column">
            <slot name="actions" :item="item" :index="index"></slot>
          </td>
        </tr>
      </tbody>
      <tfoot v-if="$slots.footer">
        <tr>
          <slot name="footer" :columns="columns"></slot>
        </tr>
      </tfoot>
    </table>
    <div v-if="items.length === 0" class="no-data">
      <slot name="no-data">No data available</slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BaseTable',
  props: {
    columns: {
      type: Array,
      required: true,
      // Each column should have { key, label, format (optional), headerClass (optional), cellClass (optional) }
    },
    items: {
      type: Array,
      default: () => []
    },
    hasActions: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    formatValue(value, formatter) {
      if (!formatter) return value;
      
      if (typeof formatter === 'function') {
        return formatter(value);
      }
      
      switch (formatter) {
        case 'currency':
          return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
          }).format(value || 0);
        case 'date':
          return value ? new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          }).format(new Date(value)) : '';
        default:
          return value;
      }
    }
  }
}
</script>

<style scoped>
.base-table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.base-table {
  width: 100%;
  border-collapse: collapse;
  margin: var(--space-sm) 0;
}

.base-table th, .base-table td {
  padding: var(--space-sm);
  text-align: left;
  border-bottom: 1px solid var(--table-border-color);
}

.base-table th {
  background-color: var(--table-header-bg);
  font-weight: var(--font-weight-bold);
}

.base-table tr:hover {
  background-color: var(--table-row-hover);
}

.actions-column {
  white-space: nowrap;
  text-align: center;
}

.no-data {
  text-align: center;
  padding: var(--space-lg);
  color: var(--color-text-secondary);
  font-style: italic;
}
</style>