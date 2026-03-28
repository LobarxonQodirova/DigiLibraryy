<template>
  <div class="catalog-browser">
    <div class="browser-sidebar">
      <h3 class="sidebar-title">Categories</h3>
      <CategoryTree
        :categories="genres"
        :selected-slug="selectedGenre"
        @select="handleGenreSelect"
      />
    </div>

    <div class="browser-main">
      <div class="browser-header">
        <h2>{{ currentCatalogName }}</h2>
        <div class="browser-controls">
          <select v-model="sortBy" class="sort-select" @change="onSort">
            <option value="title">Title (A-Z)</option>
            <option value="-title">Title (Z-A)</option>
            <option value="-publication_date">Newest First</option>
            <option value="publication_date">Oldest First</option>
            <option value="-average_rating">Highest Rated</option>
          </select>
          <div class="view-toggle">
            <button :class="{ active: viewMode === 'grid' }" @click="viewMode = 'grid'">Grid</button>
            <button :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'">List</button>
          </div>
        </div>
      </div>

      <div :class="['catalog-results', viewMode]">
        <slot :books="filteredBooks" :view-mode="viewMode" />
      </div>

      <div v-if="filteredBooks.length === 0 && !loading" class="empty-catalog">
        <p>No books found in this category.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import CategoryTree from './CategoryTree.vue'

export default {
  name: 'CatalogBrowser',
  components: { CategoryTree },
  props: {
    genres: { type: Array, default: () => [] },
    books: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    catalogName: { type: String, default: 'All Books' },
  },
  emits: ['genre-select', 'sort-change'],
  setup(props, { emit }) {
    const selectedGenre = ref('')
    const sortBy = ref('title')
    const viewMode = ref('grid')

    const currentCatalogName = computed(() => {
      if (selectedGenre.value) {
        const genre = props.genres.find((g) => g.slug === selectedGenre.value)
        return genre ? genre.name : props.catalogName
      }
      return props.catalogName
    })

    const filteredBooks = computed(() => props.books)

    const handleGenreSelect = (slug) => {
      selectedGenre.value = slug
      emit('genre-select', slug)
    }

    const onSort = () => {
      emit('sort-change', sortBy.value)
    }

    return {
      selectedGenre, sortBy, viewMode, currentCatalogName,
      filteredBooks, handleGenreSelect, onSort,
    }
  },
}
</script>

<style scoped>
.catalog-browser {
  display: flex;
  gap: 24px;
}

.browser-sidebar {
  width: 240px;
  flex-shrink: 0;
}

.sidebar-title {
  font-size: 1rem;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--primary);
}

.browser-main {
  flex: 1;
}

.browser-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.browser-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.sort-select {
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 0.85rem;
}

.view-toggle {
  display: flex;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  overflow: hidden;
}
.view-toggle button {
  background: white;
  border: none;
  padding: 6px 14px;
  font-size: 0.8rem;
}
.view-toggle button.active {
  background: var(--primary);
  color: white;
}

.empty-catalog {
  text-align: center;
  padding: 48px;
  color: var(--text-muted);
}
</style>
