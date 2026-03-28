<template>
  <div class="book-reader">
    <div class="reader-toolbar">
      <button class="toolbar-btn" @click="$emit('close')">Close</button>
      <span class="reader-title">{{ title }}</span>
      <div class="reader-controls">
        <button class="toolbar-btn" :disabled="currentPage <= 1" @click="prevPage">
          Previous
        </button>
        <span class="page-indicator">
          Page {{ currentPage }} / {{ totalPages }}
        </span>
        <button class="toolbar-btn" :disabled="currentPage >= totalPages" @click="nextPage">
          Next
        </button>
      </div>
      <div class="reader-actions">
        <button class="toolbar-btn" @click="toggleBookmark">
          {{ isBookmarked ? 'Bookmarked' : 'Bookmark' }}
        </button>
        <select v-model="fontSize" class="font-select">
          <option value="14">Small</option>
          <option value="16">Medium</option>
          <option value="20">Large</option>
          <option value="24">X-Large</option>
        </select>
      </div>
    </div>

    <div class="reader-content" :style="{ fontSize: fontSize + 'px' }">
      <div class="reading-area">
        <p v-if="!content" class="placeholder-text">
          E-book content would be rendered here. This component supports
          EPUB/PDF viewing with configurable font size, bookmarking, and
          progress tracking.
        </p>
        <div v-else v-html="content"></div>
      </div>
    </div>

    <div class="reader-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
      <span class="progress-label">{{ progressPercent.toFixed(0) }}% complete</span>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'

export default {
  name: 'BookReader',
  props: {
    title: { type: String, default: '' },
    content: { type: String, default: '' },
    initialPage: { type: Number, default: 1 },
    totalPages: { type: Number, default: 1 },
    bookmarks: { type: Array, default: () => [] },
  },
  emits: ['close', 'page-change', 'bookmark', 'progress-update'],
  setup(props, { emit }) {
    const currentPage = ref(props.initialPage)
    const fontSize = ref(16)
    const startTime = ref(Date.now())

    const progressPercent = computed(() => {
      if (props.totalPages <= 0) return 0
      return (currentPage.value / props.totalPages) * 100
    })

    const isBookmarked = computed(() =>
      props.bookmarks.some((b) => b.page === currentPage.value)
    )

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
        emitProgress()
      }
    }

    const nextPage = () => {
      if (currentPage.value < props.totalPages) {
        currentPage.value++
        emitProgress()
      }
    }

    const toggleBookmark = () => {
      emit('bookmark', {
        page: currentPage.value,
        label: `Page ${currentPage.value}`,
      })
    }

    const emitProgress = () => {
      const elapsed = Math.floor((Date.now() - startTime.value) / 1000)
      emit('progress-update', {
        current_page: currentPage.value,
        total_pages: props.totalPages,
        time_spent_seconds: elapsed,
      })
      emit('page-change', currentPage.value)
    }

    // Track reading time on unmount
    onBeforeUnmount(() => {
      emitProgress()
    })

    // Keyboard navigation
    const handleKeydown = (e) => {
      if (e.key === 'ArrowLeft') prevPage()
      if (e.key === 'ArrowRight') nextPage()
      if (e.key === 'Escape') emit('close')
    }

    onMounted(() => window.addEventListener('keydown', handleKeydown))
    onBeforeUnmount(() => window.removeEventListener('keydown', handleKeydown))

    return {
      currentPage, fontSize, progressPercent, isBookmarked,
      prevPage, nextPage, toggleBookmark,
    }
  },
}
</script>

<style scoped>
.book-reader {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #faf8f5;
}

.reader-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 20px;
  background: var(--bg-dark);
  color: white;
}

.toolbar-btn {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  color: white;
  padding: 6px 14px;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
}
.toolbar-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.reader-title {
  font-weight: 600;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.reader-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-indicator {
  font-size: 0.85rem;
  min-width: 100px;
  text-align: center;
}

.reader-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.font-select {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: none;
  padding: 6px 10px;
  border-radius: 4px;
}

.reader-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  justify-content: center;
}

.reading-area {
  max-width: 720px;
  padding: 40px 32px;
  line-height: 1.8;
  color: #333;
}

.placeholder-text {
  color: var(--text-muted);
  font-style: italic;
  text-align: center;
  padding: 48px 0;
}

.reader-progress {
  padding: 8px 20px;
  background: white;
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary);
  transition: width 0.3s;
}

.progress-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  min-width: 90px;
  text-align: right;
}
</style>
