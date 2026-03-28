<template>
  <div class="book-card" @click="$router.push(`/books/${book.id}`)">
    <div class="book-cover">
      <img
        v-if="book.cover_image"
        :src="book.cover_image"
        :alt="book.title"
        class="cover-img"
      />
      <div v-else class="cover-placeholder">
        <span>{{ book.title.charAt(0) }}</span>
      </div>
      <span
        v-if="book.available_copies_count > 0"
        class="availability-badge available"
      >
        Available
      </span>
      <span v-else class="availability-badge unavailable">Unavailable</span>
    </div>

    <div class="book-info">
      <h3 class="book-title">{{ book.title }}</h3>
      <p class="book-authors">
        {{ authorNames }}
      </p>
      <div class="book-meta">
        <span v-if="book.publication_date" class="meta-item">
          {{ formatYear(book.publication_date) }}
        </span>
        <span v-if="book.average_rating > 0" class="meta-item rating">
          &#9733; {{ Number(book.average_rating).toFixed(1) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'BookCard',
  props: {
    book: { type: Object, required: true },
  },
  setup(props) {
    const authorNames = computed(() => {
      if (props.book.authors_detail && props.book.authors_detail.length > 0) {
        return props.book.authors_detail.map((a) => a.full_name || `${a.first_name} ${a.last_name}`).join(', ')
      }
      return 'Unknown Author'
    })

    const formatYear = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).getFullYear()
    }

    return { authorNames, formatYear }
  },
}
</script>

<style scoped>
.book-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}
.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.book-cover {
  position: relative;
  height: 220px;
  background: #e9ecef;
  overflow: hidden;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  font-weight: 700;
  color: white;
  background: var(--primary);
}

.availability-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}
.availability-badge.available {
  background: var(--success);
  color: white;
}
.availability-badge.unavailable {
  background: var(--danger);
  color: white;
}

.book-info {
  padding: 14px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.book-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-authors {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.book-meta {
  display: flex;
  gap: 12px;
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: auto;
}

.rating {
  color: #f5a623;
  font-weight: 600;
}
</style>
