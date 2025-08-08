<template>
  <div class="streets-panel">
    <h3>Street Statistics</h3>
    <div class="filter-controls">
      <button
        @click="clearStreetFilter"
        :class="['filter-btn', { active: !selectedStreet }]"
      >
        All Streets
      </button>
    </div>
    <div class="streets-list">
      <div
        v-for="street in streetsList.slice(0, 10)"
        :key="street.street_name"
        :class="['street-item', { selected: selectedStreet === street.street_name }]"
        @click="selectStreet(street.street_name)"
      >
        <div class="street-name">{{ truncateStreetName(street.street_name) }}</div>
        <div class="street-stats">
          <span class="available">{{ street.available_bays }} available</span>
          <span class="total">/ {{ street.total_bays }} total</span>
        </div>
        <div class="occupancy-bar">
          <div
            class="occupancy-fill"
            :style="{ width: (100 - street.occupancy_rate) + '%' }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StreetsPanel',
  props: {
    streetsList: {
      type: Array,
      default: () => []
    },
    selectedStreet: {
      type: String,
      default: null
    }
  },
  emits: ['selectStreet', 'clearStreetFilter'],
  methods: {
    truncateStreetName(name) {
      return name && name.length > 40 ? name.substring(0, 40) + '...' : name
    },
    selectStreet(streetName) {
      this.$emit('selectStreet', streetName)
    },
    clearStreetFilter() {
      this.$emit('clearStreetFilter')
    }
  }
}
</script>

<style scoped>
.streets-panel {
  background-color: white;
  padding: 1rem 2rem;
  border-top: 1px solid #ddd;
}

.streets-panel h3 {
  color: #2c3e50;
  margin: 0 0 1rem 0;
}

.filter-controls {
  margin-bottom: 1rem;
}

.filter-btn {
  background-color: #ecf0f1;
  color: #2c3e50;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  background-color: #bdc3c7;
}

.filter-btn.active {
  background-color: #3498db;
  color: white;
}

.streets-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 0.8rem;
}

.street-item {
  background-color: #f8f9fa;
  padding: 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.street-item:hover {
  background-color: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.street-item.selected {
  border-color: #3498db;
  background-color: #ebf3fd;
  box-shadow: 0 4px 8px rgba(52, 152, 219, 0.2);
}

.street-name {
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.street-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  margin-bottom: 0.5rem;
}

.available {
  color: #27ae60;
  font-weight: bold;
}

.total {
  color: #7f8c8d;
}

.occupancy-bar {
  height: 4px;
  background-color: #e74c3c;
  border-radius: 2px;
  overflow: hidden;
}

.occupancy-fill {
  height: 100%;
  background-color: #27ae60;
  transition: width 0.3s ease;
}
</style>
