<template>
  <div class="borrowing-history">
    <h3>Borrowing History</h3>

    <div v-if="history.length === 0" class="empty-history">
      <p>No borrowing history found.</p>
    </div>

    <table v-else class="history-table">
      <thead>
        <tr>
          <th>Book</th>
          <th>Checkout Date</th>
          <th>Return Date</th>
          <th>Status</th>
          <th>Fine</th>
          <th>Rating</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="entry in history" :key="entry.id">
          <td>
            <router-link v-if="entry.book_detail" :to="`/books/${entry.book_detail.id}`">
              {{ entry.book_detail.title }}
            </router-link>
            <span v-else>Unknown Book</span>
          </td>
          <td>{{ formatDate(entry.checkout_date) }}</td>
          <td>{{ entry.return_date ? formatDate(entry.return_date) : 'Still Active' }}</td>
          <td>
            <span class="status-badge" :class="entry.was_overdue ? 'overdue' : 'normal'">
              {{ entry.was_overdue ? 'Overdue' : 'On Time' }}
            </span>
          </td>
          <td>
            <span v-if="entry.fine_amount > 0" class="fine-amount">
              ${{ Number(entry.fine_amount).toFixed(2) }}
            </span>
            <span v-else class="no-fine">--</span>
          </td>
          <td>
            <span v-if="entry.rating" class="rating">
              &#9733; {{ entry.rating }}/5
            </span>
            <button v-else class="rate-btn" @click="$emit('rate', entry)">
              Rate
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'BorrowingHistory',
  props: {
    history: { type: Array, default: () => [] },
  },
  emits: ['rate'],
  setup() {
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
      })
    }
    return { formatDate }
  },
}
</script>

<style scoped>
.borrowing-history h3 {
  margin-bottom: 16px;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.history-table th,
.history-table td {
  padding: 12px 16px;
  text-align: left;
  font-size: 0.9rem;
  border-bottom: 1px solid var(--border-color);
}

.history-table th {
  background: var(--bg-light);
  font-weight: 600;
  font-size: 0.8rem;
  text-transform: uppercase;
  color: var(--text-muted);
}

.status-badge {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}
.status-badge.normal {
  background: #d4edda;
  color: #155724;
}
.status-badge.overdue {
  background: #f8d7da;
  color: #721c24;
}

.fine-amount {
  color: var(--danger);
  font-weight: 600;
}
.no-fine {
  color: var(--text-muted);
}

.rating {
  color: #f5a623;
}

.rate-btn {
  background: var(--primary);
  color: white;
  border: none;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.empty-history {
  text-align: center;
  padding: 32px;
  color: var(--text-muted);
}
</style>
