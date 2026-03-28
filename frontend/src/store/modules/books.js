import { bookApi } from '../../api/bookApi'

const state = {
  books: [],
  currentBook: null,
  genres: [],
  authors: [],
  totalBooks: 0,
  currentPage: 1,
  pageSize: 20,
  loading: false,
  error: null,
  searchQuery: '',
  filters: {
    language: '',
    genre: '',
    available_only: false,
  },
}

const mutations = {
  SET_BOOKS(state, { results, count, page, pageSize }) {
    state.books = results
    state.totalBooks = count
    state.currentPage = page
    state.pageSize = pageSize
  },
  SET_CURRENT_BOOK(state, book) {
    state.currentBook = book
  },
  SET_GENRES(state, genres) {
    state.genres = genres
  },
  SET_AUTHORS(state, authors) {
    state.authors = authors
  },
  SET_BOOKS_LOADING(state, loading) {
    state.loading = loading
  },
  SET_BOOKS_ERROR(state, error) {
    state.error = error
  },
  SET_SEARCH_QUERY(state, query) {
    state.searchQuery = query
  },
  SET_FILTERS(state, filters) {
    state.filters = { ...state.filters, ...filters }
  },
  RESET_FILTERS(state) {
    state.filters = { language: '', genre: '', available_only: false }
    state.searchQuery = ''
  },
}

const actions = {
  async fetchBooks({ commit, state }, { page = 1, search = '' } = {}) {
    commit('SET_BOOKS_LOADING', true)
    commit('SET_BOOKS_ERROR', null)
    try {
      const params = {
        page,
        page_size: state.pageSize,
        search: search || state.searchQuery,
      }
      if (state.filters.language) params.language = state.filters.language
      if (state.filters.genre) params.genres__slug = state.filters.genre

      const response = await bookApi.getBooks(params)
      commit('SET_BOOKS', {
        results: response.data.results,
        count: response.data.count,
        page,
        pageSize: state.pageSize,
      })
      return response.data
    } catch (error) {
      commit('SET_BOOKS_ERROR', error.response?.data?.message || 'Failed to fetch books.')
      throw error
    } finally {
      commit('SET_BOOKS_LOADING', false)
    }
  },

  async fetchBookDetail({ commit }, bookId) {
    commit('SET_BOOKS_LOADING', true)
    try {
      const response = await bookApi.getBook(bookId)
      commit('SET_CURRENT_BOOK', response.data)
      return response.data
    } catch (error) {
      commit('SET_BOOKS_ERROR', 'Failed to load book details.')
      throw error
    } finally {
      commit('SET_BOOKS_LOADING', false)
    }
  },

  async fetchGenres({ commit }) {
    try {
      const response = await bookApi.getGenres()
      commit('SET_GENRES', response.data.results || response.data)
    } catch (error) {
      console.error('Failed to load genres:', error)
    }
  },

  async fetchAuthors({ commit }, search = '') {
    try {
      const response = await bookApi.getAuthors({ search })
      commit('SET_AUTHORS', response.data.results || response.data)
    } catch (error) {
      console.error('Failed to load authors:', error)
    }
  },

  setSearchQuery({ commit, dispatch }, query) {
    commit('SET_SEARCH_QUERY', query)
    dispatch('fetchBooks', { page: 1, search: query })
  },

  applyFilters({ commit, dispatch }, filters) {
    commit('SET_FILTERS', filters)
    dispatch('fetchBooks', { page: 1 })
  },

  resetFilters({ commit, dispatch }) {
    commit('RESET_FILTERS')
    dispatch('fetchBooks', { page: 1 })
  },
}

const getters = {
  allBooks: (state) => state.books,
  currentBook: (state) => state.currentBook,
  allGenres: (state) => state.genres,
  totalPages: (state) => Math.ceil(state.totalBooks / state.pageSize),
  booksLoading: (state) => state.loading,
  booksError: (state) => state.error,
  activeFilters: (state) => state.filters,
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}
