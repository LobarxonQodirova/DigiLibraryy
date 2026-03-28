import { borrowApi } from '../../api/borrowApi'

const state = {
  loans: [],
  reservations: [],
  history: [],
  fines: [],
  loading: false,
  error: null,
}

const mutations = {
  SET_LOANS(state, loans) {
    state.loans = loans
  },
  SET_RESERVATIONS(state, reservations) {
    state.reservations = reservations
  },
  SET_HISTORY(state, history) {
    state.history = history
  },
  SET_FINES(state, fines) {
    state.fines = fines
  },
  SET_BORROWING_LOADING(state, loading) {
    state.loading = loading
  },
  SET_BORROWING_ERROR(state, error) {
    state.error = error
  },
  UPDATE_LOAN(state, updatedLoan) {
    const idx = state.loans.findIndex((l) => l.id === updatedLoan.id)
    if (idx !== -1) state.loans.splice(idx, 1, updatedLoan)
  },
  REMOVE_RESERVATION(state, reservationId) {
    state.reservations = state.reservations.filter((r) => r.id !== reservationId)
  },
}

const actions = {
  async fetchLoans({ commit }) {
    commit('SET_BORROWING_LOADING', true)
    try {
      const response = await borrowApi.getLoans()
      commit('SET_LOANS', response.data.results || response.data)
    } catch (error) {
      commit('SET_BORROWING_ERROR', 'Failed to fetch loans.')
    } finally {
      commit('SET_BORROWING_LOADING', false)
    }
  },

  async checkout({ commit, dispatch }, { bookCopyId, userId, notes }) {
    commit('SET_BORROWING_LOADING', true)
    commit('SET_BORROWING_ERROR', null)
    try {
      const payload = { book_copy_id: bookCopyId, notes: notes || '' }
      if (userId) payload.user_id = userId
      const response = await borrowApi.checkout(payload)
      await dispatch('fetchLoans')
      return response.data
    } catch (error) {
      const message = error.response?.data?.error || 'Checkout failed.'
      commit('SET_BORROWING_ERROR', message)
      throw error
    } finally {
      commit('SET_BORROWING_LOADING', false)
    }
  },

  async renewLoan({ commit }, borrowingId) {
    commit('SET_BORROWING_ERROR', null)
    try {
      const response = await borrowApi.renew({ borrowing_id: borrowingId })
      commit('UPDATE_LOAN', response.data)
      return response.data
    } catch (error) {
      const message = error.response?.data?.error || 'Renewal failed.'
      commit('SET_BORROWING_ERROR', message)
      throw error
    }
  },

  async returnBook({ commit, dispatch }, { borrowingId, conditionOnReturn, damageNotes }) {
    commit('SET_BORROWING_LOADING', true)
    try {
      const response = await borrowApi.returnBook({
        borrowing_id: borrowingId,
        condition_on_return: conditionOnReturn || 'good',
        damage_notes: damageNotes || '',
      })
      await dispatch('fetchLoans')
      return response.data
    } catch (error) {
      commit('SET_BORROWING_ERROR', error.response?.data?.error || 'Return failed.')
      throw error
    } finally {
      commit('SET_BORROWING_LOADING', false)
    }
  },

  async fetchReservations({ commit }) {
    try {
      const response = await borrowApi.getReservations()
      commit('SET_RESERVATIONS', response.data.results || response.data)
    } catch (error) {
      console.error('Failed to fetch reservations:', error)
    }
  },

  async createReservation({ commit, dispatch }, { bookId, notes }) {
    try {
      const response = await borrowApi.createReservation({ book: bookId, notes })
      await dispatch('fetchReservations')
      return response.data
    } catch (error) {
      commit('SET_BORROWING_ERROR', error.response?.data?.message || 'Reservation failed.')
      throw error
    }
  },

  async cancelReservation({ commit }, reservationId) {
    try {
      await borrowApi.cancelReservation(reservationId)
      commit('REMOVE_RESERVATION', reservationId)
    } catch (error) {
      commit('SET_BORROWING_ERROR', 'Failed to cancel reservation.')
      throw error
    }
  },

  async fetchHistory({ commit }) {
    try {
      const response = await borrowApi.getHistory()
      commit('SET_HISTORY', response.data.results || response.data)
    } catch (error) {
      console.error('Failed to fetch borrowing history:', error)
    }
  },

  async fetchFines({ commit }) {
    try {
      const response = await borrowApi.getFines()
      commit('SET_FINES', response.data.results || response.data)
    } catch (error) {
      console.error('Failed to fetch fines:', error)
    }
  },

  async payFine({ commit, dispatch }, { fineId, amount, paymentMethod }) {
    try {
      const response = await borrowApi.payFine(fineId, { amount, payment_method: paymentMethod })
      await dispatch('fetchFines')
      return response.data
    } catch (error) {
      commit('SET_BORROWING_ERROR', error.response?.data?.error || 'Payment failed.')
      throw error
    }
  },
}

const getters = {
  activeLoans: (state) => state.loans.filter((l) => l.status === 'active'),
  overdueLoans: (state) => state.loans.filter((l) => l.is_overdue),
  pendingReservations: (state) => state.reservations.filter((r) => r.status === 'pending'),
  unpaidFines: (state) => state.fines.filter((f) => ['pending', 'partial'].includes(f.status)),
  totalFinesOwed: (state) =>
    state.fines
      .filter((f) => ['pending', 'partial'].includes(f.status))
      .reduce((sum, f) => sum + parseFloat(f.balance || 0), 0),
  borrowingLoading: (state) => state.loading,
  borrowingError: (state) => state.error,
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}
