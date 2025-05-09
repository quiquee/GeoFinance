import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Import the main CSS framework
import './styles/main.css'

// Create the Vue application
const app = createApp(App)

// Use the router
app.use(router)

// Mount the app to the DOM
app.mount('#app')