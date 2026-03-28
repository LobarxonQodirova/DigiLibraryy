import api from '../../api/axiosConfig'

const TOKEN_KEY = 'digilibrary_access_token'
const REFRESH_KEY = 'digilibrary_refresh_token'

const state = {
  user: null,
  accessToken: localStorage.getItem(TOKEN_KEY) || null,
  refreshToken: localStorage.getItem(REFRESH_KEY) || null,
  loading: false,
  error: null,
}

const mutations = {
  SET_USER(state, user) {
    state.user = user
  },
  SET_TOKENS(state, { access, refresh }) {
    state.accessToken = access
    state.refreshToken = refresh
    localStorage.setItem(TOKEN_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
  },
  CLEAR_AUTH(state) {
    state.user = null
    state.accessToken = null
    state.refreshToken = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
  SET_AUTH_LOADING(state, loading) {
    state.loading = loading
  },
  SET_AUTH_ERROR(state, error) {
    state.error = error
  },
}

const actions = {
  async login({ commit, dispatch }, credentials) {
    commit('SET_AUTH_LOADING', true)
    commit('SET_AUTH_ERROR', null)
    try {
      const response = await api.post('/auth/login/', credentials)
      commit('SET_TOKENS', {
        access: response.data.access,
        refresh: response.data.refresh,
      })
      await dispatch('fetchProfile')
      return response.data
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed. Please check your credentials.'
      commit('SET_AUTH_ERROR', message)
      throw error
    } finally {
      commit('SET_AUTH_LOADING', false)
    }
  },

  async register({ commit, dispatch }, userData) {
    commit('SET_AUTH_LOADING', true)
    commit('SET_AUTH_ERROR', null)
    try {
      const response = await api.post('/auth/register/', userData)
      if (response.data.tokens) {
        commit('SET_TOKENS', {
          access: response.data.tokens.access,
          refresh: response.data.tokens.refresh,
        })
        commit('SET_USER', response.data.user)
      }
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || 'Registration failed.'
      commit('SET_AUTH_ERROR', message)
      throw error
    } finally {
      commit('SET_AUTH_LOADING', false)
    }
  },

  async fetchProfile({ commit, state }) {
    if (!state.accessToken) return
    try {
      const response = await api.get('/auth/profile/')
      commit('SET_USER', response.data)
    } catch (error) {
      if (error.response?.status === 401) {
        commit('CLEAR_AUTH')
      }
    }
  },

  async logout({ commit, state }) {
    try {
      if (state.refreshToken) {
        await api.post('/auth/logout/', { refresh: state.refreshToken })
      }
    } catch {
      // Ignore errors during logout
    } finally {
      commit('CLEAR_AUTH')
    }
  },

  async changePassword({ commit }, { oldPassword, newPassword }) {
    try {
      const response = await api.put('/auth/change-password/', {
        old_password: oldPassword,
        new_password: newPassword,
      })
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || 'Password change failed.'
      commit('SET_AUTH_ERROR', message)
      throw error
    }
  },

  async refreshAccessToken({ commit, state }) {
    try {
      const response = await api.post('/auth/token/refresh/', {
        refresh: state.refreshToken,
      })
      commit('SET_TOKENS', {
        access: response.data.access,
        refresh: response.data.refresh || state.refreshToken,
      })
      return response.data.access
    } catch (error) {
      commit('CLEAR_AUTH')
      throw error
    }
  },
}

const getters = {
  isAuthenticated: (state) => !!state.accessToken && !!state.user,
  currentUser: (state) => state.user,
  userRole: (state) => state.user?.role || null,
  isAdmin: (state) => state.user?.role === 'admin',
  isLibrarian: (state) => ['admin', 'librarian'].includes(state.user?.role),
  isMember: (state) => state.user?.role === 'member',
  authError: (state) => state.error,
  authLoading: (state) => state.loading,
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}
