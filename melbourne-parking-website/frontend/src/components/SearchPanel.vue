<template>
  <div class="search-panel">
    <!-- Display Mode Selection -->
    <div class="mode-selection">
      <button
        @click="setDisplayMode('heatmap')"
        :class="['mode-btn', { active: displayMode === 'heatmap' }]"
      >
        Heatmap
      </button>
      <button
        @click="setDisplayMode('parking')"
        :class="['mode-btn', { active: displayMode === 'parking' }]"
      >
        Parking
      </button>
      <button
        @click="setDisplayMode('analytics')"
        :class="['mode-btn', { active: displayMode === 'analytics' }]"
      >
        Analytics
      </button>
    </div>

    <!-- Mode-specific content -->

    <!-- Heatmap Mode -->
    <div v-if="displayMode === 'heatmap'" class="mode-content">
      <div class="mode-description">
        <p>View parking availability density across the city</p>
        <div class="heatmap-legend">
          <h5>Legend:</h5>
          <div class="legend-item">
            <span class="legend-color hot"></span>
            <span>High availability</span>
          </div>
          <div class="legend-item">
            <span class="legend-color cold"></span>
            <span>Low availability</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Parking Mode (formerly Streets Mode) -->
    <div v-if="displayMode === 'parking'" class="mode-content">
      <div class="mode-description">
        <p>Browse parking by street and view all available spots</p>
      </div>

      <!-- Street Search -->
      <div class="search-input-wrapper">
        <input
          v-model="searchQuery"
          @input="handleSearchInput"
          @focus="showSuggestions = true"
          @blur="handleSearchBlur"
          @keydown.enter="selectFirstSuggestion"
          @keydown.down="navigateSuggestions(1)"
          @keydown.up="navigateSuggestions(-1)"
          type="text"
          placeholder="🔍 Search streets... (e.g. Collins Street)"
          class="search-input"
        />
        <button v-if="searchQuery" @click="clearSearch" class="clear-search-btn">×</button>
      </div>

      <!-- Search Suggestions Dropdown -->
      <div v-if="showSuggestions && filteredSuggestions.length > 0" class="suggestions-dropdown">
        <div
          v-for="(suggestion, index) in filteredSuggestions"
          :key="suggestion.street_name"
          :class="['suggestion-item', { active: selectedSuggestionIndex === index }]"
          @mousedown="selectSuggestion(suggestion)"
          @mouseenter="selectedSuggestionIndex = index"
        >
          <div class="suggestion-name">{{ truncateStreetName(suggestion.street_name) }}</div>
          <div class="suggestion-stats">
            <span class="available">{{ suggestion.available_bays }}</span> available /
            <span class="total">{{ suggestion.total_bays }}</span> total
          </div>
        </div>
      </div>
    </div>

    <!-- Analytics Mode -->
    <div v-if="displayMode === 'analytics'" class="mode-content">
      <div class="mode-description">
        <p>Analyze parking data and population trends</p>
      </div>

      <!-- Integrated Analytics Panel Component -->
      <AnalyticsPanel :parkingData="parkingData" />
    </div>

    <!-- Selected Parking Bay Details (shown for all modes) -->
    <div v-if="selectedParkingBay" class="selected-bay">
      <h4>🅿️ Selected Parking</h4>
      <div class="bay-details">
        <div class="detail-row">
          <span class="label">ID:</span>
          <span class="value">{{ selectedParkingBay.kerbside_id }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Status:</span>
          <span class="value" :class="selectedParkingBay.status === 'Unoccupied' ? 'available' : 'occupied'">
            {{ selectedParkingBay.status === 'Unoccupied' ? '✅ Available' : '❌ Occupied' }}
          </span>
        </div>
        <div class="detail-row">
          <span class="label">Location:</span>
          <span class="value">{{ selectedParkingBay.road_segment || 'Unknown' }}</span>
        </div>
        <div class="detail-row" v-if="selectedParkingBay.zone_number">
          <span class="label">Zone:</span>
          <span class="value">{{ selectedParkingBay.zone_number }}</span>
        </div>
        <div class="detail-row" v-if="selectedParkingBay.distance">
          <span class="label">Distance:</span>
          <span class="value">{{ selectedParkingBay.distance }}m away</span>
        </div>
      </div>

      <!-- Navigation and Actions -->
      <div class="bay-actions">
        <button @click="getDirections" class="action-btn directions-btn">
          📍 Get Directions
        </button>
        <button @click="clearSelection" class="action-btn clear-btn">
          Clear Selection
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import AnalyticsPanel from './AnalyticsPanel.vue'

export default {
  name: 'SearchPanel',
  components: {
    AnalyticsPanel
  },
  props: {
    nearbyResults: {
      type: Array,
      default: () => []
    },
    selectedParkingBay: {
      type: Object,
      default: null
    },
    streetsList: {
      type: Array,
      default: () => []
    },
    parkingData: {
      type: Array,
      default: () => []
    }
  },
  emits: ['findParking', 'selectBay', 'clearSelection', 'selectStreet', 'toggleHeatmap', 'setDisplayMode'],
  data() {
    return {
      displayMode: 'parking', // Changed default mode from 'streets' to 'parking'
      searchQuery: '',
      showSuggestions: false,
      selectedSuggestionIndex: -1,
      isSearching: false
    }
  },
  computed: {
    filteredSuggestions() {
      if (!this.searchQuery || this.searchQuery.length < 1) return [] // 将最小字符要求从2改为1

      const query = this.searchQuery.toLowerCase().trim()

      // 确保 streetsList 存在且是数组
      if (!this.streetsList || !Array.isArray(this.streetsList) || this.streetsList.length === 0) {
        console.warn('Streets list is empty or invalid', this.streetsList)
        return []
      }

      console.log(`Searching for "${query}" in ${this.streetsList.length} streets`)

      // 更灵活的搜索匹配
      const matchingStreets = this.streetsList.filter(street => {
        // 确保 street 和 street_name 存在
        if (!street || !street.street_name) return false

        const streetName = street.street_name.toLowerCase()
        // 使�� includes 而不是精确匹配，这样可以查找部分匹配
        return streetName.includes(query)
      })

      console.log(`Found ${matchingStreets.length} matching streets`)

      return matchingStreets
        .slice(0, 8) // 增加显示数量以便找到更多匹配
        .sort((a, b) => {
          // 优先显示更精确的匹配
          const aExact = a.street_name.toLowerCase() === query
          const bExact = b.street_name.toLowerCase() === query

          if (aExact && !bExact) return -1
          if (!aExact && bExact) return 1

          // 其次，优先显示以搜索词开头的街道
          const aStartsWith = a.street_name.toLowerCase().startsWith(query)
          const bStartsWith = b.street_name.toLowerCase().startsWith(query)

          if (aStartsWith && !bStartsWith) return -1
          if (!aStartsWith && bStartsWith) return 1

          // 然后按可用车位排序
          if (a.available_bays !== b.available_bays) {
            return b.available_bays - a.available_bays
          }

          // 最后按字母顺序排序
          return a.street_name.localeCompare(b.street_name)
        })
    }
  },
  methods: {
    setDisplayMode(mode) {
      this.displayMode = mode
      this.$emit('setDisplayMode', mode)

      // Clear search when switching to heatmap mode
      if (mode === 'heatmap') {
        this.clearSearch()
        this.$emit('toggleHeatmap', true)
      } else {
        this.$emit('toggleHeatmap', false)
      }
    },

    showAllStreets() {
      this.clearSearch()
      this.$emit('selectStreet', null)
    },

    handleSearchInput() {
      this.selectedSuggestionIndex = -1
      this.showSuggestions = true
    },

    handleSearchBlur() {
      // Delay hiding suggestions to allow for click events
      setTimeout(() => {
        this.showSuggestions = false
      }, 200)
    },

    navigateSuggestions(direction) {
      if (this.filteredSuggestions.length === 0) return

      this.selectedSuggestionIndex += direction

      if (this.selectedSuggestionIndex < -1) {
        this.selectedSuggestionIndex = this.filteredSuggestions.length - 1
      } else if (this.selectedSuggestionIndex >= this.filteredSuggestions.length) {
        this.selectedSuggestionIndex = -1
      }
    },

    selectFirstSuggestion() {
      if (this.filteredSuggestions.length > 0) {
        const suggestion = this.selectedSuggestionIndex >= 0
          ? this.filteredSuggestions[this.selectedSuggestionIndex]
          : this.filteredSuggestions[0]
        this.selectSuggestion(suggestion)
      }
    },

    selectSuggestion(suggestion) {
      this.searchQuery = suggestion.street_name
      this.showSuggestions = false
      this.$emit('selectStreet', suggestion.street_name)
    },

    clearSearch() {
      this.searchQuery = ''
      this.showSuggestions = false
      this.$emit('selectStreet', null)
    },

    selectParkingBay(bay) {
      this.$emit('selectBay', bay)
    },

    clearSelection() {
      this.$emit('clearSelection')
    },

    getDirections() {
      if (!this.selectedParkingBay) return

      // Open Google Maps with directions using lat/lon properties
      const lat = this.selectedParkingBay.lat || this.selectedParkingBay.latitude
      const lng = this.selectedParkingBay.lon || this.selectedParkingBay.longitude

      if (lat && lng) {
        const destination = `${lat},${lng}`
        const googleMapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${destination}&travelmode=driving`
        window.open(googleMapsUrl, '_blank')
      }
    },

    truncateStreetName(name) {
      return name && name.length > 35 ? name.substring(0, 35) + '...' : name
    }
  }
}
</script>

<style scoped>
.search-panel {
  width: 280px;
  background-color: white;
  padding: 1rem;
  border-radius: 8px;
  height: fit-content;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-panel h3 {
  color: #2c3e50;
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
}

/* Mode Selection */
.mode-selection {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.mode-btn {
  background-color: #ecf0f1;
  color: #2c3e50;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
  flex: 1;
  margin: 0 0.1rem;
}

.mode-btn.active {
  background-color: #3498db;
  color: white;
}

.mode-description {
  font-size: 0.9rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

/* Search Section */
.search-section {
  margin-bottom: 1rem;
}

.search-input-wrapper {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 0.6rem 2.2rem 0.6rem 0.8rem;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #2c3e50;
}

.clear-search-btn {
  position: absolute;
  right: 0.5rem;
  top: 0.5rem;
  background: none;
  border: none;
  color: #7f8c8d;
  font-size: 1.2rem;
  cursor: pointer;
}

.suggestions-dropdown {
  background-color: white;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  margin-top: 0.2rem;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.suggestion-item {
  padding: 0.6rem 0.8rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.suggestion-item:hover {
  background-color: #f1f1f1;
}

.suggestion-item.active {
  background-color: #3498db;
  color: white;
}

.suggestion-name {
  font-size: 0.9rem;
  color: #2c3e50;
}

.suggestion-stats {
  font-size: 0.8rem;
  color: #7f8c8d;
}

/* Primary and Secondary Action Buttons */
.primary-action-btn {
  width: 100%;
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: bold;
  margin: 0.5rem 0;
  transition: background-color 0.2s;
}

.primary-action-btn:hover:not(:disabled) {
  background-color: #2980b9;
}

.primary-action-btn:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.secondary-action-btn {
  width: 100%;
  background-color: #95a5a6;
  color: white;
  border: none;
  padding: 0.6rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  margin: 0.5rem 0;
  transition: background-color 0.2s;
}

.secondary-action-btn:hover {
  background-color: #7f8c8d;
}

/* Selected Bay Styles */
.selected-bay {
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 0.8rem;
  margin-bottom: 1rem;
}

.selected-bay h4 {
  color: #2c3e50;
  margin: 0 0 0.8rem 0;
  font-size: 1rem;
}

.bay-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.3rem 0;
  border-bottom: 1px solid #ecf0f1;
}

.detail-row:last-child {
  border-bottom: none;
}

.label {
  font-weight: bold;
  color: #7f8c8d;
  font-size: 0.85rem;
}

.value {
  font-size: 0.85rem;
  color: #2c3e50;
  text-align: right;
}

.value.available {
  color: #27ae60;
  font-weight: bold;
}

.value.occupied {
  color: #e74c3c;
  font-weight: bold;
}

.bay-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
}

.action-btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background-color 0.2s;
}

.action-btn:hover {
  background-color: #2980b9;
}

/* Default State */
.default-state p {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  text-align: center;
}

.quick-actions {
  text-align: center;
}

.quick-action-btn {
  background-color: #95a5a6;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  margin: 0.2rem 0;
  transition: background-color 0.2s;
}

.quick-action-btn:hover {
  background-color: #7f8c8d;
}

/* Nearby Results */
.nearby-results {
  border-top: 1px solid #ecf0f1;
  padding-top: 1rem;
  margin-top: 1rem;
}

.nearby-results h4 {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  border: 1px solid #ecf0f1;
}

.result-item:hover {
  background-color: #e9ecef;
  border-color: #3498db;
}

.result-status {
  font-size: 1.2rem;
  min-width: 1.5rem;
}

.result-info {
  flex: 1;
}

.result-status.available {
  color: #27ae60;
}

.result-status.occupied {
  color: #e74c3c;
}

/* Mode content styling */
.mode-content {
  margin-bottom: 1rem;
}

.mode-content p {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-bottom: 0.8rem;
  line-height: 1.4;
}

/* Heatmap legend styling */
.heatmap-legend h5 {
  margin: 0.5rem 0 0.3rem 0;
  color: #2c3e50;
  font-size: 0.85rem;
}

.legend-color.cold {
  background-color: #e74c3c;
}
</style>
