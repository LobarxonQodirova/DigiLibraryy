<template>
  <footer class="app-footer">
    <div class="footer-content">
      <div class="footer-brand">
        <strong>DigiLibrary</strong> &mdash; Digital Library Management System
      </div>
      <div class="footer-links">
        <router-link to="/catalog">Catalog</router-link>
        <router-link to="/search">Search</router-link>
        <a href="/api/docs/" target="_blank" rel="noopener">API Docs</a>
      </div>
      <div class="footer-copy">
        &copy; {{ currentYear }} DigiLibrary. All rights reserved.
      </div>
    </div>
  </footer>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'AppFooter',
  setup() {
    const currentYear = computed(() => new Date().getFullYear())
    return { currentYear }
  },
}
</script>

<style scoped>
.app-footer {
  background: var(--bg-dark);
  color: rgba(255, 255, 255, 0.75);
  padding: 20px 24px;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.footer-brand {
  font-size: 0.9rem;
}

.footer-links {
  display: flex;
  gap: 16px;
}
.footer-links a {
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  font-size: 0.85rem;
}
.footer-links a:hover {
  color: white;
  text-decoration: none;
}

.footer-copy {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.4);
}
</style>
