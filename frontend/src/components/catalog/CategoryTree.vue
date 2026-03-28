<template>
  <ul class="category-tree">
    <li
      v-for="category in categories"
      :key="category.id || category.slug"
      class="category-item"
    >
      <button
        class="category-btn"
        :class="{ active: selectedSlug === category.slug }"
        @click="$emit('select', category.slug)"
      >
        <span class="expand-icon" v-if="hasChildren(category)" @click.stop="toggleExpand(category.slug)">
          {{ expandedSlugs.has(category.slug) ? '&#9660;' : '&#9654;' }}
        </span>
        <span v-else class="expand-spacer"></span>
        <span class="category-name">{{ category.name }}</span>
      </button>

      <CategoryTree
        v-if="hasChildren(category) && expandedSlugs.has(category.slug)"
        :categories="category.children"
        :selected-slug="selectedSlug"
        class="subtree"
        @select="(slug) => $emit('select', slug)"
      />
    </li>
  </ul>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'CategoryTree',
  props: {
    categories: { type: Array, default: () => [] },
    selectedSlug: { type: String, default: '' },
  },
  emits: ['select'],
  setup() {
    const expandedSlugs = ref(new Set())

    const hasChildren = (category) => {
      return category.children && category.children.length > 0
    }

    const toggleExpand = (slug) => {
      if (expandedSlugs.value.has(slug)) {
        expandedSlugs.value.delete(slug)
      } else {
        expandedSlugs.value.add(slug)
      }
    }

    return { expandedSlugs, hasChildren, toggleExpand }
  },
}
</script>

<style scoped>
.category-tree {
  list-style: none;
  padding: 0;
  margin: 0;
}

.subtree {
  padding-left: 16px;
}

.category-item {
  margin-bottom: 2px;
}

.category-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  padding: 8px 10px;
  border-radius: 4px;
  text-align: left;
  font-size: 0.9rem;
  color: var(--text-primary);
  cursor: pointer;
  transition: background 0.15s;
}
.category-btn:hover {
  background: var(--bg-light);
}
.category-btn.active {
  background: var(--primary);
  color: white;
}

.expand-icon {
  font-size: 0.7rem;
  width: 14px;
  text-align: center;
  cursor: pointer;
}

.expand-spacer {
  width: 14px;
}

.category-name {
  flex: 1;
}
</style>
