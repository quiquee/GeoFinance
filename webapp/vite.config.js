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
    host: '127.0.0.1', // Force Vite to use 127.0.0.1 instead of localhost
    hmr: {
      overlay: true, // Show errors as an overlay
      timeout: 1000, // Increase timeout for slow connections
    },
},
    watch: {
      usePolling: false, // Use native file system events instead of polling (more efficient)
      interval: 100     // Polling interval in ms (only used if usePolling is true)
    },
  
})