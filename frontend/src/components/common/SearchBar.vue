<template>
  <div class="search-bar" :class="{ focused: isFocused }">
    <input
      ref="inputRef"
      v-model="query"
      type="text"
      placeholder="Search books, authors, ISBN..."
      class="search-input"
      @input="onInput"
      @focus="isFocused = true"
      @blur="onBlur"
      @keydown.enter="submitSearch"
      @keydown.escape="closeSuggestions"
    />
    <button class="search-btn" @click="submitSearch">Search</button>

    <ul v-if="showSuggestions && suggestions.length > 0" class="suggestions-list">
      <li
        v-for="(suggestion, idx) in suggestions"
        :key="idx"
        class="suggestion-item"
        @mousedown.prevent="selectSuggestion(suggestion)"
      >
        <span class="suggestion-type">{{ suggestion.type }}</span>
        <span class="suggestion-text">{{ suggestion.text }}</span>
      </li>
    </ul>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { bookApi } from '../../api/bookApi'

export default {
  name: 'SearchBar',
  setup() {
    const router = useRouter()
    const query = ref('')
    const suggestions = ref([])
    const isFocused = ref(false)
    const inputRef = ref(null)
    let debounceTimer = null

    const showSuggestions = computed(() => isFocused.value && suggestions.value.length > 0)

    const onInput = () => {
      clearTimeout(debounceTimer)
      if (query.value.length < 2) {
        suggestions.value = []
        return
      }
      debounceTimer = setTimeout(async () => {
        try {
          const response = await bookApi.getSearchSuggestions(query.value)
          suggestions.value = response.data.suggestions || []
        } catch {
          suggestions.value = []
        }
      }, 300)
    }

    const submitSearch = () => {
      if (query.value.trim()) {
        suggestions.value = []
        isFocused.value = false
        router.push({ name: 'Search', query: { q: query.value.trim() } })
      }
    }

    const selectSuggestion = (suggestion) => {
      query.value = suggestion.text
      submitSearch()
    }

    const closeSuggestions = () => {
      suggestions.value = []
      isFocused.value = false
    }

    const onBlur = () => {
      setTimeout(() => {
        isFocused.value = false
      }, 200)
    }

    return {
      query, suggestions, isFocused, inputRef, showSuggestions,
      onInput, submitSearch, selectSuggestion, closeSuggestions, onBlur,
    }
  },
}
</script>

<style scoped>
.search-bar {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  transition: background 0.2s;
}
.search-bar.focused {
  background: rgba(255, 255, 255, 0.25);
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: white;
  padding: 8px 14px;
  font-size: 0.9rem;
}
.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.search-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 0 6px 6px 0;
  font-weight: 500;
}
.search-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.suggestions-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-radius: 0 0 6px 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  list-style: none;
  margin-top: 2px;
  z-index: 100;
  max-height: 300px;
  overflow-y: auto;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  color: var(--text-primary);
}
.suggestion-item:hover {
  background: var(--bg-light);
}

.suggestion-type {
  font-size: 0.7rem;
  text-transform: uppercase;
  background: var(--primary);
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  min-width: 50px;
  text-align: center;
}

.suggestion-text {
  font-size: 0.9rem;
}
</style>
