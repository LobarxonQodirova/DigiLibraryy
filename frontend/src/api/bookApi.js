import api from './axiosConfig'

export const bookApi = {
  // Books
  getBooks(params = {}) {
    return api.get('/books/items/', { params })
  },

  getBook(id) {
    return api.get(`/books/items/${id}/`)
  },

  createBook(data) {
    return api.post('/books/items/', data)
  },

  updateBook(id, data) {
    return api.patch(`/books/items/${id}/`, data)
  },

  deleteBook(id) {
    return api.delete(`/books/items/${id}/`)
  },

  getBookCopies(bookId) {
    return api.get(`/books/items/${bookId}/copies/`)
  },

  getBookEditions(bookId) {
    return api.get(`/books/items/${bookId}/editions/`)
  },

  // Genres
  getGenres(params = {}) {
    return api.get('/books/genres/', { params })
  },

  getGenre(slug) {
    return api.get(`/books/genres/${slug}/`)
  },

  createGenre(data) {
    return api.post('/books/genres/', data)
  },

  // Authors
  getAuthors(params = {}) {
    return api.get('/books/authors/', { params })
  },

  getAuthor(id) {
    return api.get(`/books/authors/${id}/`)
  },

  getAuthorBooks(authorId) {
    return api.get(`/books/authors/${authorId}/books/`)
  },

  createAuthor(data) {
    return api.post('/books/authors/', data)
  },

  // Publishers
  getPublishers(params = {}) {
    return api.get('/books/publishers/', { params })
  },

  // Book copies
  getCopies(params = {}) {
    return api.get('/books/copies/', { params })
  },

  updateCopyStatus(copyId, status) {
    return api.post(`/books/copies/${copyId}/update-status/`, { status })
  },

  // Search
  searchBooks(query, filters = {}) {
    return api.get('/search/books/', { params: { q: query, ...filters } })
  },

  getSearchSuggestions(query) {
    return api.get('/search/suggest/', { params: { q: query } })
  },
}

export default bookApi
