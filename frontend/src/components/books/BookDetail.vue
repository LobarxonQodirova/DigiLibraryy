<template>
  <div v-if="book" class="book-detail">
    <div class="book-header">
      <div class="cover-section">
        <img
          v-if="book.cover_image"
          :src="book.cover_image"
          :alt="book.title"
          class="detail-cover"
        />
        <div v-else class="detail-cover-placeholder">
          {{ book.title.charAt(0) }}
        </div>
      </div>

      <div class="info-section">
        <h1 class="title">{{ book.title }}</h1>
        <h2 v-if="book.subtitle" class="subtitle">{{ book.subtitle }}</h2>

        <div class="authors">
          <span v-for="(author, idx) in book.authors_detail" :key="author.id">
            <router-link :to="`/search?author=${author.id}`">{{ author.full_name }}</router-link>
            <span v-if="idx < book.authors_detail.length - 1">, </span>
          </span>
        </div>

        <div class="meta-grid">
          <div v-if="book.publisher_name" class="meta-row">
            <span class="meta-label">Publisher</span>
            <span class="meta-value">{{ book.publisher_name }}</span>
          </div>
          <div v-if="book.publication_date" class="meta-row">
            <span class="meta-label">Published</span>
            <span class="meta-value">{{ formatDate(book.publication_date) }}</span>
          </div>
          <div v-if="book.isbn_detail" class="meta-row">
            <span class="meta-label">ISBN</span>
            <span class="meta-value">{{ book.isbn_detail.isbn_13 || book.isbn_detail.isbn_10 }}</span>
          </div>
          <div v-if="book.page_count" class="meta-row">
            <span class="meta-label">Pages</span>
            <span class="meta-value">{{ book.page_count }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-label">Language</span>
            <span class="meta-value">{{ book.language }}</span>
          </div>
        </div>

        <div class="availability-section">
          <span class="copies-info">
            {{ book.available_copies_count }} of {{ book.total_copies_count }} copies available
          </span>
        </div>

        <div v-if="book.average_rating > 0" class="rating-section">
          <span class="rating-stars">&#9733; {{ Number(book.average_rating).toFixed(1) }}</span>
          <span class="rating-count">({{ book.total_ratings }} ratings)</span>
        </div>

        <div class="action-buttons">
          <button
            v-if="book.available_copies_count > 0"
            class="btn btn-primary"
            @click="$emit('borrow', book)"
          >
            Borrow This Book
          </button>
          <button v-else class="btn btn-secondary" @click="$emit('reserve', book)">
            Place Reservation
          </button>
          <button class="btn btn-outline" @click="$emit('add-to-list', book)">
            Add to Reading List
          </button>
        </div>
      </div>
    </div>

    <div v-if="book.description" class="book-description">
      <h3>Description</h3>
      <p>{{ book.description }}</p>
    </div>

    <div v-if="book.genres_detail && book.genres_detail.length > 0" class="book-genres">
      <h3>Genres</h3>
      <div class="genre-tags">
        <router-link
          v-for="genre in book.genres_detail"
          :key="genre.id"
          :to="`/catalog?genre=${genre.slug}`"
          class="genre-tag"
        >
          {{ genre.name }}
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BookDetail',
  props: {
    book: { type: Object, default: null },
  },
  emits: ['borrow', 'reserve', 'add-to-list'],
  setup() {
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    }
    return { formatDate }
  },
}
</script>

<style scoped>
.book-detail {
  max-width: 900px;
}

.book-header {
  display: flex;
  gap: 32px;
  margin-bottom: 32px;
}

.detail-cover {
  width: 250px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.detail-cover-placeholder {
  width: 250px;
  height: 350px;
  background: var(--primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  font-weight: 700;
  border-radius: 8px;
}

.title {
  font-size: 1.8rem;
  margin-bottom: 4px;
}

.subtitle {
  font-size: 1.1rem;
  color: var(--text-muted);
  font-weight: 400;
  margin-bottom: 12px;
}

.authors {
  font-size: 1rem;
  margin-bottom: 16px;
}
.authors a {
  color: var(--primary);
}

.meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 16px;
}

.meta-row {
  display: flex;
  gap: 8px;
}

.meta-label {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--text-muted);
  min-width: 80px;
}

.meta-value {
  font-size: 0.9rem;
}

.copies-info {
  font-weight: 600;
  color: var(--success);
}

.rating-section {
  margin: 8px 0;
}

.rating-stars {
  color: #f5a623;
  font-size: 1.1rem;
  font-weight: 600;
}

.rating-count {
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-left: 4px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 24px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9rem;
  border: none;
}
.btn-primary {
  background: var(--primary);
  color: white;
}
.btn-secondary {
  background: var(--secondary);
  color: white;
}
.btn-outline {
  background: transparent;
  border: 2px solid var(--primary);
  color: var(--primary);
}

.book-description,
.book-genres {
  margin-bottom: 24px;
}

.book-description h3,
.book-genres h3 {
  font-size: 1.2rem;
  margin-bottom: 8px;
}

.genre-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.genre-tag {
  background: var(--bg-light);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  color: var(--primary);
  text-decoration: none;
}
.genre-tag:hover {
  background: var(--primary);
  color: white;
  text-decoration: none;
}
</style>
