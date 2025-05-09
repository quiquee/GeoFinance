<template>
  <div class="financial-banner">
    <div v-if="loading" class="loading-indicator">
      <span>Loading financial data...</span>
    </div>
    <div v-else-if="error" class="error-indicator">
      <span>{{ error }}</span>
    </div>
    <div v-else class="marquee-container">
      <div class="marquee-content" ref="marqueeContent">
        <div class="financial-stats" ref="financialStats">
          <div class="stat-item">
            <span class="stat-label">Total Assets:</span>
            <span class="stat-value" :class="totalAssets >= 0 ? 'positive' : 'negative'">{{ formatCurrency(totalAssets) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Total Liabilities:</span>
            <span class="stat-value" :class="totalLiabilities > 0 ? 'negative' : 'positive'">{{ formatCurrency(totalLiabilities) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Total Income:</span>
            <span class="stat-value" :class="totalIncome >= 0 ? 'positive' : 'negative'">{{ formatCurrency(totalIncome) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Total Expenses:</span>
            <span class="stat-value" :class="totalExpenses > 0 ? 'negative' : 'positive'">{{ formatCurrency(totalExpenses) }}</span>
          </div>
          <div class="stat-item total-wealth">
            <span class="stat-label">Total Wealth:</span>
            <span class="stat-value" :class="totalWealth >= 0 ? 'positive' : 'negative'">{{ formatCurrency(totalWealth) }}</span>
          </div>
        </div>
        <!-- Clone for smooth infinite scrolling -->
        <div class="financial-stats clone">
          <div class="stat-item">
            <span class="stat-label">Total Assets:</span>
            <span class="stat-value" :class="totalAssets >= 0 ? 'positive' : 'negative'">{{ formatCurrency(totalAssets) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Total Liabilities:</span>
            <span class="stat-value" :class="totalLiabilities > 0 ? 'negative' : 'positive'">{{ formatCurrency(totalLiabilities) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Total Income:</span>
            <span class="stat-value" :class="totalIncome >= 0 ? 'positive' : 'negative'">{{ formatCurrency(totalIncome) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Total Expenses:</span>
            <span class="stat-value" :class="totalExpenses > 0 ? 'negative' : 'positive'">{{ formatCurrency(totalExpenses) }}</span>
          </div>
          <div class="stat-item total-wealth">
            <span class="stat-label">Total Wealth:</span>
            <span class="stat-value" :class="totalWealth >= 0 ? 'positive' : 'negative'">{{ formatCurrency(totalWealth) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { buildApiUrl } from '../config/api';
import { getAuthHeaders } from '../services/authService';
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';

export default {
  name: 'FinancialBanner',
  setup() {
    const loading = ref(true);
    const error = ref(null);
    const totalAssets = ref(0);
    const totalLiabilities = ref(0);
    const totalIncome = ref(0);
    const totalExpenses = ref(0);
    const refreshTimer = ref(null);
    const marqueeContent = ref(null);
    const financialStats = ref(null);
    const scrollInterval = ref(null);
    const animationSpeed = 30; // Lower is faster
    
    const totalWealth = computed(() => {
      return totalAssets.value - totalLiabilities.value;
    });
    
    const fetchFinancialData = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const response = await fetch(buildApiUrl('api/ledger/trial-balance'), {
          headers: getAuthHeaders(),
          credentials: 'include'
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch financial data');
        }
        
        const data = await response.json();
        calculateTotals(data);
        loading.value = false;
      } catch (err) {
        console.error('Error fetching trial balance data:', err);
        error.value = 'Unable to load financial summary';
        loading.value = false;
      }
    };
    
    const calculateTotals = (data) => {
      let assets = 0;
      let liabilities = 0;
      let income = 0;
      let expenses = 0;
      
      if (data && data.trial_balance) {
        data.trial_balance.forEach(account => {
          const debitBalance = parseFloat(account.debit_balance) || 0;
          const creditBalance = parseFloat(account.credit_balance) || 0;
          
          switch(account.account_type) {
            case 'asset':
              assets += debitBalance - creditBalance + 1;
              break;
            case 'liability':
              liabilities += creditBalance - debitBalance;
              break;
            case 'income':
              income += creditBalance - debitBalance;
              break;
            case 'expense':
              expenses += debitBalance - creditBalance;
              break;
          }
        });
      }
      
      totalAssets.value = assets;
      totalLiabilities.value = liabilities;
      totalIncome.value = income;
      totalExpenses.value = expenses;
    };
    
    const formatCurrency = (value) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value);
    };
    
    const startRefreshTimer = () => {
      refreshTimer.value = setInterval(() => {
        fetchFinancialData();
      }, 60000); // Refresh every 60 seconds (1 minute)
    };
    
    // Expose refresh method to be called after POST operations
    const refreshData = () => {
      fetchFinancialData();
    };
    
    // Start marquee animation
    const startMarquee = () => {
      if (!marqueeContent.value || !financialStats.value) return;
      
      let scrollPos = 0;
      const contentWidth = financialStats.value.offsetWidth;
      
      // Clear any existing interval
      if (scrollInterval.value) {
        clearInterval(scrollInterval.value);
      }
      
      scrollInterval.value = setInterval(() => {
        scrollPos++;
        marqueeContent.value.style.transform = `translateX(-${scrollPos}px)`;
        
        // Reset position when first copy is scrolled out
        if (scrollPos >= contentWidth) {
          scrollPos = 0;
          marqueeContent.value.style.transform = 'translateX(0)';
        }
      }, animationSpeed);
    };
    
    onMounted(() => {
      fetchFinancialData();
      startRefreshTimer();
      
      // Add event listener for custom event that will be triggered after POST requests
      window.addEventListener('financial-data-updated', refreshData);
      
      // Start the marquee after a short delay to ensure the DOM is fully rendered
      setTimeout(() => {
        startMarquee();
      }, 500);
      
      // Restart marquee when window is resized
      window.addEventListener('resize', () => {
        startMarquee();
      });
    });
    
    onBeforeUnmount(() => {
      // Clean up timers and event listeners when component is unmounted
      if (refreshTimer.value) {
        clearInterval(refreshTimer.value);
      }
      if (scrollInterval.value) {
        clearInterval(scrollInterval.value);
      }
      window.removeEventListener('financial-data-updated', refreshData);
      window.removeEventListener('resize', startMarquee);
    });
    
    return {
      loading,
      error,
      totalAssets,
      totalLiabilities,
      totalIncome,
      totalExpenses,
      totalWealth,
      formatCurrency,
      refreshData,
      marqueeContent,
      financialStats
    };
  }
}
</script>

<style scoped>
.financial-banner {
  
  padding: 8px 15px;
  
  width: 100%;
  overflow: hidden;
  position: relative;
}

.marquee-container {
  width: 95%;
  height: 30px;
  overflow: hidden;
}

.marquee-content {
  display: flex;
  white-space: nowrap;
  will-change: transform;
}

.financial-stats {
  display: inline-flex;
  flex-wrap: nowrap;
  align-items: center;
}

.financial-stats.clone {
  margin-left: 20px; /* Space between original and clone */
}

.stat-item {
  display: inline-flex;
  align-items: center;
  padding: 0 15px;
  border-right: 1px solid #ddd;
  height: 30px;
}

.stat-item:first-child {
  padding-left: 0;
}

.stat-item:last-child {
  border-right: none;
}

.stat-label {
  font-weight: 500;
  margin-right: 5px;
  white-space: nowrap;
}

.stat-value {
  font-weight: 600;
}

.total-wealth {
  font-weight: 600;
}

.total-wealth .stat-label {
  font-weight: 600;
}

.total-wealth .stat-value {
  font-weight: 700;
}

.positive {
  color: #28a745;
}

.negative {
  color: #dc3545;
}

.loading-indicator, .error-indicator {
  text-align: center;
  padding: 5px;
  font-size: 0.9rem;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-indicator {
  color: #dc3545;
}
</style>