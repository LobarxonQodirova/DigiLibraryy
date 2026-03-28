import api from './axiosConfig'

export const memberApi = {
  // Profile
  getProfile() {
    return api.get('/auth/profile/')
  },

  updateProfile(data) {
    return api.patch('/auth/profile/', data)
  },

  changePassword(data) {
    return api.put('/auth/change-password/', data)
  },

  // Users (admin)
  getUsers(params = {}) {
    return api.get('/auth/users/', { params })
  },

  getUser(id) {
    return api.get(`/auth/users/${id}/`)
  },

  toggleUserActive(id) {
    return api.post(`/auth/users/${id}/toggle-active/`)
  },

  changeUserRole(id, role) {
    return api.post(`/auth/users/${id}/change-role/`, { role })
  },

  // Membership cards
  getMembershipCards(params = {}) {
    return api.get('/members/cards/', { params })
  },

  reportCardLost(cardId) {
    return api.post(`/members/cards/${cardId}/report-lost/`)
  },

  // Reading lists
  getReadingLists(params = {}) {
    return api.get('/members/reading-lists/', { params })
  },

  getReadingList(id) {
    return api.get(`/members/reading-lists/${id}/`)
  },

  createReadingList(data) {
    return api.post('/members/reading-lists/', data)
  },

  updateReadingList(id, data) {
    return api.patch(`/members/reading-lists/${id}/`, data)
  },

  deleteReadingList(id) {
    return api.delete(`/members/reading-lists/${id}/`)
  },

  addBookToList(listId, bookId, options = {}) {
    return api.post(`/members/reading-lists/${listId}/add-book/`, {
      book_id: bookId,
      ...options,
    })
  },

  removeBookFromList(listId, bookId) {
    return api.delete(`/members/reading-lists/${listId}/remove-book/${bookId}/`)
  },

  // Dashboard / reports (admin)
  getDashboard() {
    return api.get('/reports/dashboard/')
  },

  getPopularBooks(days = 30, limit = 10) {
    return api.get('/reports/popular-books/', { params: { days, limit } })
  },

  getMemberActivity(days = 30) {
    return api.get('/reports/member-activity/', { params: { days } })
  },
}

export default memberApi
