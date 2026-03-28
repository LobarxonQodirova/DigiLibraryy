<template>
  <div id="digilibrary-app">
    <Navbar v-if="showNavbar" />
    <div class="app-layout">
      <Sidebar v-if="showSidebar" />
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
    <Footer v-if="showFooter" />
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import Navbar from './components/common/Navbar.vue'
import Sidebar from './components/common/Sidebar.vue'
import Footer from './components/common/Footer.vue'

export default {
  name: 'App',
  components: { Navbar, Sidebar, Footer },
  setup() {
    const route = useRoute()
    const store = useStore()

    const showNavbar = computed(() => route.meta.hideNavbar !== true)
    const showSidebar = computed(() => store.getters['auth/isAuthenticated'] && route.meta.hideSidebar !== true)
    const showFooter = computed(() => route.meta.hideFooter !== true)

    return { showNavbar, showSidebar, showFooter }
  },
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary: #2c5f8a;
  --primary-light: #4a8bc2;
  --secondary: #6c757d;
  --success: #28a745;
  --warning: #ffc107;
  --danger: #dc3545;
  --bg-light: #f8f9fa;
  --bg-dark: #343a40;
  --text-primary: #212529;
  --text-muted: #6c757d;
  --border-color: #dee2e6;
  --sidebar-width: 250px;
  --navbar-height: 60px;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: var(--text-primary);
  background-color: var(--bg-light);
  line-height: 1.6;
}

#digilibrary-app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-layout {
  display: flex;
  flex: 1;
  margin-top: var(--navbar-height);
}

.main-content {
  flex: 1;
  padding: 24px;
  min-height: calc(100vh - var(--navbar-height) - 60px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

a {
  color: var(--primary);
  text-decoration: none;
}
a:hover {
  color: var(--primary-light);
  text-decoration: underline;
}

button {
  cursor: pointer;
}
</style>
