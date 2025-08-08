<template>
  <header class="header">
    <h1>Melbourne Parking System</h1>
    <button @click="$emit('refresh')" :disabled="isLoading" class="refresh-btn">
      {{ isLoading ? 'Loading...' : 'Refresh Data' }}
    </button>
  </header>
</template>

<script>
export default {
  name: 'HeaderComponent',
  props: {
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh']
}
</script>

<style scoped>
.header {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  font-size: 1.5rem;
  margin: 0;
}

.refresh-btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #2980b9;
}

.refresh-btn:disabled {
  background-color: #7f8c8d;
  cursor: not-allowed;
}
</style>
