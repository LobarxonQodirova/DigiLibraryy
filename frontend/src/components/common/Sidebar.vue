<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <button class="sidebar-toggle" @click="toggle">
      {{ isCollapsed ? '&#9654;' : '&#9664;' }}
    </button>

    <nav class="sidebar-nav">
      <div class="sidebar-section">
        <h4 v-if="!isCollapsed" class="section-title">Browse</h4>
        <router-link to="/catalog" class="sidebar-link">
          <span class="icon">&#128218;</span>
          <span v-if="!isCollapsed" class="label">Catalog</span>
        </router-link>
        <router-link to="/search" class="sidebar-link">
          <span class="icon">&#128269;</span>
          <span v-if="!isCollapsed" class="label">Search</span>
        </router-link>
      </div>

      <div v-if="isAuthenticated" class="sidebar-section">
        <h4 v-if="!isCollapsed" class="section-title">My Library</h4>
        <router-link to="/my-books" class="sidebar-link">
          <span class="icon">&#128214;</span>
          <span v-if="!isCollapsed" class="label">My Books</span>
        </router-link>
      </div>

      <div v-if="isStaff" class="sidebar-section">
        <h4 v-if="!isCollapsed" class="section-title">Administration</h4>
        <router-link to="/admin" class="sidebar-link">
          <span class="icon">&#9881;</span>
          <span v-if="!isCollapsed" class="label">Dashboard</span>
        </router-link>
      </div>

      <div v-if="isAuthenticated" class="sidebar-section sidebar-stats">
        <h4 v-if="!isCollapsed" class="section-title">Quick Stats</h4>
        <div v-if="!isCollapsed" class="stat-item">
          <span class="stat-label">Active Loans</span>
          <span class="stat-value">{{ activeLoansCount }}</span>
        </div>
        <div v-if="!isCollapsed" class="stat-item">
          <span class="stat-label">Reservations</span>
          <span class="stat-value">{{ reservationsCount }}</span>
        </div>
      </div>
    </nav>
  </aside>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'Sidebar',
  setup() {
    const store = useStore()

    const isCollapsed = computed(() => store.getters.sidebarCollapsed)
    const isAuthenticated = computed(() => store.getters['auth/isAuthenticated'])
    const isStaff = computed(() => store.getters['auth/isLibrarian'])
    const activeLoansCount = computed(() => store.getters['borrowing/activeLoans'].length)
    const reservationsCount = computed(() => store.getters['borrowing/pendingReservations'].length)

    const toggle = () => store.commit('TOGGLE_SIDEBAR')

    return { isCollapsed, isAuthenticated, isStaff, activeLoansCount, reservationsCount, toggle }
  },
}
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  min-height: calc(100vh - var(--navbar-height));
  background: white;
  border-right: 1px solid var(--border-color);
  padding: 16px 0;
  transition: width 0.25s;
  overflow: hidden;
}
.sidebar.collapsed {
  width: 60px;
}

.sidebar-toggle {
  display: block;
  margin: 0 auto 12px;
  background: none;
  border: none;
  font-size: 1rem;
  color: var(--text-muted);
  padding: 4px 8px;
}

.section-title {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  padding: 12px 20px 4px;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  color: var(--text-primary);
  text-decoration: none;
  transition: background 0.15s;
}
.sidebar-link:hover,
.sidebar-link.router-link-active {
  background: var(--bg-light);
  color: var(--primary);
  text-decoration: none;
}

.icon {
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}

.sidebar-stats {
  margin-top: auto;
  border-top: 1px solid var(--border-color);
  padding-top: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 20px;
  font-size: 0.85rem;
}
.stat-label {
  color: var(--text-muted);
}
.stat-value {
  font-weight: 600;
}
</style>
