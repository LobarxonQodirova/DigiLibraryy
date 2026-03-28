import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

import HomeView from '../views/HomeView.vue'
import CatalogView from '../views/CatalogView.vue'
import BookDetailView from '../views/BookDetailView.vue'
import MyBooksView from '../views/MyBooksView.vue'
import AdminView from '../views/AdminView.vue'
import SearchView from '../views/SearchView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: { title: 'DigiLibrary - Home' },
  },
  {
    path: '/catalog',
    name: 'Catalog',
    component: CatalogView,
    meta: { title: 'Browse Catalog' },
  },
  {
    path: '/books/:id',
    name: 'BookDetail',
    component: BookDetailView,
    meta: { title: 'Book Details' },
    props: true,
  },
  {
    path: '/search',
    name: 'Search',
    component: SearchView,
    meta: { title: 'Search' },
  },
  {
    path: '/my-books',
    name: 'MyBooks',
    component: MyBooksView,
    meta: { title: 'My Books', requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminView,
    meta: { title: 'Admin Dashboard', requiresAuth: true, requiresStaff: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/HomeView.vue'),
    meta: { title: 'Login', hideNavbar: false },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: {
      template: `
        <div class="not-found">
          <h1>404</h1>
          <p>The page you are looking for does not exist.</p>
          <router-link to="/">Return Home</router-link>
        </div>
      `,
    },
    meta: { title: 'Page Not Found' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  },
})

// Navigation guards
router.beforeEach((to, from, next) => {
  // Set document title
  document.title = to.meta.title || 'DigiLibrary'

  const isAuthenticated = store.getters['auth/isAuthenticated']
  const user = store.state.auth.user

  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }

  if (to.meta.requiresStaff && user && user.role === 'member') {
    return next({ name: 'Home' })
  }

  next()
})

export default router
