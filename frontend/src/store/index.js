import { createStore } from 'vuex'
import auth from './modules/auth'
import books from './modules/books'
import borrowing from './modules/borrowing'

const store = createStore({
  modules: {
    auth,
    books,
    borrowing,
  },

  state: {
    appLoading: false,
    globalError: null,
    sidebarCollapsed: false,
  },

  mutations: {
    SET_APP_LOADING(state, loading) {
      state.appLoading = loading
    },
    SET_GLOBAL_ERROR(state, error) {
      state.globalError = error
    },
    CLEAR_GLOBAL_ERROR(state) {
      state.globalError = null
    },
    TOGGLE_SIDEBAR(state) {
      state.sidebarCollapsed = !state.sidebarCollapsed
    },
  },

  actions: {
    setLoading({ commit }, loading) {
      commit('SET_APP_LOADING', loading)
    },
    setError({ commit }, error) {
      commit('SET_GLOBAL_ERROR', error)
      // Auto-clear after 5 seconds
      setTimeout(() => commit('CLEAR_GLOBAL_ERROR'), 5000)
    },
    clearError({ commit }) {
      commit('CLEAR_GLOBAL_ERROR')
    },
  },

  getters: {
    isLoading: (state) => state.appLoading,
    globalError: (state) => state.globalError,
    sidebarCollapsed: (state) => state.sidebarCollapsed,
  },
})

export default store
