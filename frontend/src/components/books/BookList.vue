<template>
  <div class="book-list-container">
    <div v-if="loading" class="loading-state">
      <p>Loading books...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="$emit('retry')">Try Again</button>
    </div>

    <div v-else-if="books.length === 0" class="empty-state">
      <p>No books found matching your criteria.</p>
    </div>

    <template v-else>
      <div class="book-grid">
        <BookCard v-for="book in books" :key="book.id" :book="book" />
      </div>

      <div v-if="totalPages > 1" class="pagination">
        <button
          class="page-btn"
          :disabled="currentPage <= 1"
          @click="$emit('page-change', currentPage - 1)"
        >
          Previous
        </button>

        <span class="page-info">
          Page {{ currentPage }} of {{ totalPages }}
        </span>

        <button
          class="page-btn"
          :disabled="currentPage >= totalPages"
          @click="$emit('page-change', currentPage + 1)"
        >
          Next
        </button>
      </div>
    </template>
  </div>
</template>

<script>
import BookCard from './BookCard.vue'

export default {
  name: 'BookList',
  components: { BookCard },
  props: {
    books: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    error: { type: String, default: null },
    currentPage: { type: Number, default: 1 },
    totalPages: { type: Number, default: 1 },
  },
  emits: ['page-change', 'retry'],
}
</script>

<style scoped>
.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding: 16px 0;
}

.page-btn {
  background: var(--primary);
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  font-weight: 500;
}
.page-btn:disabled {
  background: var(--secondary);
  cursor: not-allowed;
  opacity: 0.5;
}

.page-info {
  font-size: 0.9rem;
  color: var(--text-muted);
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 48px 24px;
  color: var(--text-muted);
}

.error-state button {
  margin-top: 12px;
  background: var(--primary);
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
}
</style>
