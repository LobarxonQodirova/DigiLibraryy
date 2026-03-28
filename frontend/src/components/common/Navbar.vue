<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <router-link to="/" class="logo">DigiLibrary</router-link>
    </div>

    <SearchBar class="navbar-search" />

    <div class="navbar-links">
      <router-link to="/catalog" class="nav-link">Catalog</router-link>
      <router-link to="/search" class="nav-link">Search</router-link>

      <template v-if="isAuthenticated">
        <router-link to="/my-books" class="nav-link">My Books</router-link>
        <router-link v-if="isStaff" to="/admin" class="nav-link">Admin</router-link>

        <div class="user-menu">
          <button class="user-menu-trigger" @click="showUserMenu = !showUserMenu">
            {{ userName }}
            <span class="caret">&#9662;</span>
          </button>
          <div v-if="showUserMenu" class="user-dropdown">
            <router-link to="/profile" class="dropdown-item" @click="showUserMenu = false">
              Profile
            </router-link>
            <button class="dropdown-item" @click="handleLogout">Logout</button>
          </div>
        </div>
      </template>

      <template v-else>
        <button class="btn btn-primary" @click="$router.push('/login')">Login</button>
      </template>
    </div>
  </nav>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import SearchBar from './SearchBar.vue'

export default {
  name: 'Navbar',
  components: { SearchBar },
  setup() {
    const store = useStore()
    const router = useRouter()
    const showUserMenu = ref(false)

    const isAuthenticated = computed(() => store.getters['auth/isAuthenticated'])
    const isStaff = computed(() => store.getters['auth/isLibrarian'])
    const userName = computed(() => {
      const user = store.getters['auth/currentUser']
      return user ? `${user.first_name} ${user.last_name}` : ''
    })

    const handleLogout = async () => {
      showUserMenu.value = false
      await store.dispatch('auth/logout')
      router.push('/')
    }

    return { isAuthenticated, isStaff, userName, showUserMenu, handleLogout }
  },
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--navbar-height);
  background: var(--primary);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 24px;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.navbar-brand .logo {
  font-size: 1.4rem;
  font-weight: 700;
  color: white;
  text-decoration: none;
  margin-right: 24px;
}

.navbar-search {
  flex: 1;
  max-width: 500px;
  margin: 0 24px;
}

.navbar-links {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-left: auto;
}

.nav-link {
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background 0.2s;
}
.nav-link:hover,
.nav-link.router-link-active {
  color: white;
  background: rgba(255, 255, 255, 0.15);
  text-decoration: none;
}

.user-menu {
  position: relative;
}

.user-menu-trigger {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.4);
  color: white;
  padding: 6px 14px;
  border-radius: 4px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 160px;
  margin-top: 6px;
  overflow: hidden;
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 10px 16px;
  color: var(--text-primary);
  text-decoration: none;
  text-align: left;
  background: none;
  border: none;
  font-size: 0.9rem;
  cursor: pointer;
}
.dropdown-item:hover {
  background: var(--bg-light);
}

.btn-primary {
  background: white;
  color: var(--primary);
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  font-weight: 600;
}
</style>
