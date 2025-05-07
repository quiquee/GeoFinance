import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    // Configure HMR
    hmr: {
      overlay: true, // Show errors as an overlay
      timeout: 1000, // Increase timeout for slow connections
    },
    // Configure watch options for better file monitoring
    watch: {
      usePolling: false, // Use native file system events instead of polling (more efficient)
      interval: 100     // Polling interval in ms (only used if usePolling is true)
    },
    // Open browser automatically
    open: true,
    // Proxy API requests to backend server
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true
      },
      '/ledger': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true
      }
    }
  }
});