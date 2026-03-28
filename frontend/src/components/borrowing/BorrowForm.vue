<template>
  <div class="borrow-form">
    <h3>Borrow Book</h3>

    <div v-if="availableCopies.length === 0" class="no-copies">
      <p>No copies are currently available for borrowing.</p>
      <button class="btn btn-secondary" @click="$emit('reserve')">
        Place a Reservation
      </button>
    </div>

    <form v-else @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="copy-select">Select Copy</label>
        <select id="copy-select" v-model="selectedCopyId" required class="form-control">
          <option value="" disabled>Choose a copy...</option>
          <option v-for="copy in availableCopies" :key="copy.id" :value="copy.id">
            {{ copy.barcode }} - Shelf: {{ copy.shelf_location || 'N/A' }}
            ({{ copy.condition_display }})
          </option>
        </select>
      </div>

      <div v-if="isStaff" class="form-group">
        <label for="member-id">Member (Staff Checkout)</label>
        <input
          id="member-id"
          v-model="memberId"
          type="text"
          placeholder="Enter member UUID or leave blank for self"
          class="form-control"
        />
      </div>

      <div class="form-group">
        <label for="notes">Notes (optional)</label>
        <textarea
          id="notes"
          v-model="notes"
          rows="2"
          class="form-control"
          placeholder="Any special notes..."
        ></textarea>
      </div>

      <div class="form-info">
        <p>Loan period: <strong>{{ loanPeriod }} days</strong></p>
        <p>Due date: <strong>{{ dueDate }}</strong></p>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="!selectedCopyId || loading">
          {{ loading ? 'Processing...' : 'Confirm Checkout' }}
        </button>
        <button type="button" class="btn btn-cancel" @click="$emit('cancel')">
          Cancel
        </button>
      </div>

      <p v-if="error" class="form-error">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import dayjs from 'dayjs'

export default {
  name: 'BorrowForm',
  props: {
    availableCopies: { type: Array, default: () => [] },
    loanPeriod: { type: Number, default: 14 },
  },
  emits: ['submit', 'cancel', 'reserve'],
  setup(props, { emit }) {
    const store = useStore()
    const selectedCopyId = ref('')
    const memberId = ref('')
    const notes = ref('')
    const loading = ref(false)
    const error = ref(null)

    const isStaff = computed(() => store.getters['auth/isLibrarian'])

    const dueDate = computed(() =>
      dayjs().add(props.loanPeriod, 'day').format('MMMM D, YYYY')
    )

    const handleSubmit = async () => {
      loading.value = true
      error.value = null
      try {
        await store.dispatch('borrowing/checkout', {
          bookCopyId: selectedCopyId.value,
          userId: memberId.value || undefined,
          notes: notes.value,
        })
        emit('submit')
      } catch (err) {
        error.value = err.response?.data?.error || 'Checkout failed.'
      } finally {
        loading.value = false
      }
    }

    return {
      selectedCopyId, memberId, notes, loading, error,
      isStaff, dueDate, handleSubmit,
    }
  },
}
</script>

<style scoped>
.borrow-form {
  background: white;
  border-radius: 8px;
  padding: 24px;
  max-width: 500px;
}

.borrow-form h3 {
  margin-bottom: 16px;
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

.form-info {
  background: var(--bg-light);
  padding: 12px 16px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 0.9rem;
}
.form-info p {
  margin: 4px 0;
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
.btn-secondary {
  background: var(--secondary);
  color: white;
}
.btn-cancel {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-muted);
}

.form-error {
  color: var(--danger);
  margin-top: 12px;
  font-size: 0.9rem;
}

.no-copies {
  text-align: center;
  padding: 24px;
  color: var(--text-muted);
}
</style>
