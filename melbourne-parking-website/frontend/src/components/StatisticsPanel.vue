<template>
  <div class="stats-panel">
    <div class="stat-card">
      <h3>Total Bays</h3>
      <div class="stat-number">{{ stats.total_bays || 0 }}</div>
    </div>
    <div class="stat-card available">
      <h3>Available</h3>
      <div class="stat-number">{{ stats.available_bays || 0 }}</div>
    </div>
    <div class="stat-card occupied">
      <h3>Occupied</h3>
      <div class="stat-number">{{ stats.occupied_bays || 0 }}</div>
    </div>
    <div class="stat-card rate">
      <h3>Occupancy Rate</h3>
      <div class="stat-number">{{ stats.occupancy_rate || 0 }}%</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatisticsPanel',
  props: {
    stats: {
      type: Object,
      default: () => ({})
    }
  }
}
</script>

<style scoped>
.stats-panel {
  display: flex;
  gap: 1rem;
  padding: 1rem 2rem;
  background-color: white;
  border-bottom: 1px solid #ddd;
}

.stat-card {
  flex: 1;
  text-align: center;
  padding: 1rem;
  border-radius: 8px;
  background-color: #ecf0f1;
}

.stat-card h3 {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin: 0 0 0.5rem 0;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

.stat-card.available {
  background-color: #d5f4e6;
}

.stat-card.available .stat-number {
  color: #27ae60;
}

.stat-card.occupied {
  background-color: #fadbd8;
}

.stat-card.occupied .stat-number {
  color: #e74c3c;
}

.stat-card.rate {
  background-color: #d6eaf8;
}

.stat-card.rate .stat-number {
  color: #3498db;
}
</style>
