<template>
  <header class="header">
    <div class="header-left">
      <button @click="goToHome" class="home-arrow-btn" title="Back to Home">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.42-1.41L7.83 13H20v-2z"/>
        </svg>
      </button>
      <h1>Melbourne Parking System</h1>
    </div>
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
  emits: ['refresh'],
  methods: {
    goToHome() {
      this.$router.push('/')
    }
  }
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

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header h1 {
  font-size: 1.5rem;
  margin: 0;
}

.home-arrow-btn {
  background-color: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
}

.home-arrow-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.6);
  transform: scale(1.05);
}

.home-arrow-btn svg {
  width: 20px;
  height: 20px;
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
