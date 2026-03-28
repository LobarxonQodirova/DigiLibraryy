<template>
  <div class="return-book-form">
    <h3>Return Book</h3>

    <div v-if="loan" class="loan-summary">
      <p><strong>Book:</strong> {{ loan.book_title }}</p>
      <p><strong>Checked out:</strong> {{ formatDate(loan.checkout_date) }}</p>
      <p>
        <strong>Due date:</strong>
        <span :class="{ overdue: loan.is_overdue }">{{ formatDate(loan.due_date) }}</span>
      </p>
      <p v-if="loan.is_overdue" class="overdue-warning">
        This book is {{ loan.days_overdue }} day(s) overdue.
      </p>
    </div>

    <form @submit.prevent="handleReturn">
      <div class="form-group">
        <label for="condition">Condition on Return</label>
        <select id="condition" v-model="condition" class="form-control">
          <option value="good">Good</option>
          <option value="fair">Fair</option>
          <option value="damaged">Damaged</option>
          <option value="lost">Lost</option>
        </select>
      </div>

      <div v-if="condition === 'damaged' || condition === 'lost'" class="form-group">
        <label for="damage-notes">Damage Notes</label>
        <textarea
          id="damage-notes"
          v-model="damageNotes"
          rows="3"
          class="form-control"
          placeholder="Describe the damage..."
          required
        ></textarea>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Processing...' : 'Confirm Return' }}
        </button>
        <button type="button" class="btn btn-cancel" @click="$emit('cancel')">
          Cancel
        </button>
      </div>

      <p v-if="error" class="form-error">{{ error }}</p>
      <p v-if="successMessage" class="form-success">{{ successMessage }}</p>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'ReturnBook',
  props: {
    loan: { type: Object, default: null },
  },
  emits: ['returned', 'cancel'],
  setup(props, { emit }) {
    const store = useStore()
    const condition = ref('good')
    const damageNotes = ref('')
    const loading = ref(false)
    const error = ref(null)
    const successMessage = ref(null)

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
      })
    }

    const handleReturn = async () => {
      if (!props.loan) return
      loading.value = true
      error.value = null
      successMessage.value = null
      try {
        const result = await store.dispatch('borrowing/returnBook', {
          borrowingId: props.loan.id,
          conditionOnReturn: condition.value,
          damageNotes: damageNotes.value,
        })
        successMessage.value = 'Book returned successfully.'
        if (result.fine_assessed > 0) {
          successMessage.value += ` A fine of $${Number(result.fine_assessed).toFixed(2)} was assessed.`
        }
        emit('returned', result)
      } catch (err) {
        error.value = err.response?.data?.error || 'Return failed.'
      } finally {
        loading.value = false
      }
    }

    return {
      condition, damageNotes, loading, error, successMessage,
      formatDate, handleReturn,
    }
  },
}
</script>

<style scoped>
.return-book-form {
  background: white;
  border-radius: 8px;
  padding: 24px;
  max-width: 500px;
}

.loan-summary {
  background: var(--bg-light);
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 0.9rem;
}
.loan-summary p {
  margin: 4px 0;
}

.overdue {
  color: var(--danger);
  font-weight: 600;
}

.overdue-warning {
  color: var(--danger);
  font-weight: 600;
  margin-top: 8px;
}

.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 6px;
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 0.9rem;
}

.form-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 24px;
  border-radius: 6px;
  font-weight: 600;
  border: none;
}
.btn-primary {
  background: var(--primary);
  color: white;
}
.btn-primary:disabled {
  opacity: 0.5;
}
.btn-cancel {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-muted);
}

.form-error {
  color: var(--danger);
  margin-top: 12px;
}
.form-success {
  color: var(--success);
  margin-top: 12px;
}
</style>
