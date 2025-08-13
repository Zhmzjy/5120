<template>
  <div class="analytics-page">
    
    <button class="back-btn" @click="goBack">← Back to Home</button>

    <h1>City Analytics</h1>

    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading chart...</p>
    </div>

    
    <div v-else>
      <AdvancedAnalytics />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AdvancedAnalytics from '../components/AdvancedAnalytics.vue'

export default {
  name: 'AnalyticsPage',
  components: {
    AdvancedAnalytics
  },
  setup() {
    const loading = ref(true)
    const router = useRouter()

    const goBack = () => {
      router.push('/') 
    }

    onMounted(() => {
      setTimeout(() => {
        loading.value = false
      }, 1500)
    })

    return { loading, goBack }
  }
}
</script>

<style scoped>
.analytics-page {
  padding: 20px;
}


.back-btn {
  background: linear-gradient(90deg, #007bff, #00b4d8);
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 30px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  margin-bottom: 15px;
}

.back-btn:hover {
  background: linear-gradient(90deg, #0056b3, #0096c7);
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}

.loading {
  text-align: center;
  margin-top: 50px;
}

.spinner {
  border: 4px solid rgba(0,0,0,0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #09f;
  animation: spin 1s ease infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>