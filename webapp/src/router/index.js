import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from '../services/authService'

// Import view components
// We'll use lazy loading to improve performance
const Home = () => import('../views/Home.vue')
const Accounts = () => import('../views/Accounts.vue')
const Journal = () => import('../views/Journal.vue')
const Reports = () => import('../views/Reports.vue')
const Login = () => import('../views/Login.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      public: true,
      onlyWhenLoggedOut: true
    }
  },
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/accounts',
    name: 'Accounts',
    component: Accounts,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/journal',
    name: 'Journal',
    component: Journal,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports,
    meta: {
      requiresAuth: true
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard to check authentication for protected routes
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isPublic = to.matched.some(record => record.meta.public)
  const onlyWhenLoggedOut = to.matched.some(record => record.meta.onlyWhenLoggedOut)
  
  const loggedIn = isAuthenticated()
  
  if (requiresAuth && !loggedIn) {
    // User is not authenticated, redirect to login
    return next({
      path: '/login',
      query: { redirect: to.fullPath } // Store the path user was trying to visit
    })
  }
  
  if (loggedIn && onlyWhenLoggedOut) {
    // User is authenticated but trying to access a page that should only be available when logged out
    return next('/')
  }
  
  next()
})

export default router