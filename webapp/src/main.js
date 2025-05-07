import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Create the Vue application
const app = createApp(App)

// Use the router
app.use(router)

// Mount the app to the DOM
app.mount('#app')