import api from './axiosConfig'

export const borrowApi = {
  // Loans
  getLoans(params = {}) {
    return api.get('/borrowing/loans/', { params })
  },

  getLoan(id) {
    return api.get(`/borrowing/loans/${id}/`)
  },

  checkout(data) {
    return api.post('/borrowing/loans/checkout/', data)
  },

  renew(data) {
    return api.post('/borrowing/loans/renew/', data)
  },

  returnBook(data) {
    return api.post('/borrowing/loans/return/', data)
  },

  // Reservations
  getReservations(params = {}) {
    return api.get('/borrowing/reservations/', { params })
  },

  createReservation(data) {
    return api.post('/borrowing/reservations/', data)
  },

  cancelReservation(id) {
    return api.post(`/borrowing/reservations/${id}/cancel/`)
  },

  // Borrowing history
  getHistory(params = {}) {
    return api.get('/borrowing/history/', { params })
  },

  // Fines
  getFines(params = {}) {
    return api.get('/borrowing/fines/', { params })
  },

  getFine(id) {
    return api.get(`/borrowing/fines/${id}/`)
  },

  payFine(id, data) {
    return api.post(`/borrowing/fines/${id}/pay/`, data)
  },

  waiveFine(id, reason) {
    return api.post(`/borrowing/fines/${id}/waive/`, { reason })
  },
}

export default borrowApi
