<template>
  <div class="parking-website">
    <!-- Header -->
    <HeaderComponent @refresh="refreshAllData" :isLoading="isLoading" />

    <!-- Statistics Panel -->
    <StatisticsPanel :stats="overviewStats" />

    <!-- Main Content -->
    <div class="main-content">
      <!-- Search Panel - Now smaller and shows selected parking info -->
      <SearchPanel
        :nearbyResults="nearbyResults"
        :selectedParkingBay="selectedParkingBay"
        :streetsList="streetsList"
        :parkingData="parkingData"
        @findParking="handleFindParking"
        @selectBay="handleSelectBay"
        @clearSelection="handleClearSelection"
        @selectStreet="handleSelectStreet"
        @toggleHeatmap="handleToggleHeatmap"
        @setDisplayMode="handleSetDisplayMode"
      />

      <!-- Map Container -->
      <ParkingMap
        ref="parkingMap"
        :parkingData="parkingData"
        :nearbyResults="nearbyResults"
        :selectedStreet="selectedStreet"
        :showHeatmap="showHeatmap"
        :displayMode="displayMode"
        @mapClick="handleMapClick"
        @selectParkingBay="handleSelectBay"
      />
    </div>

    <!-- Streets Panel -->
    <StreetsPanel
      :streetsList="streetsList"
      :selectedStreet="selectedStreet"
      @selectStreet="handleSelectStreet"
      @clearStreetFilter="handleClearStreetFilter"
    />
  </div>
</template>

<script>
import HeaderComponent from './components/HeaderComponent.vue'
import StatisticsPanel from './components/StatisticsPanel.vue'
import SearchPanel from './components/SearchPanel.vue'
import ParkingMap from './components/ParkingMap.vue'
import StreetsPanel from './components/StreetsPanel.vue'
import parkingService from './services/parkingService.js'

export default {
  name: 'App',
  components: {
    HeaderComponent,
    StatisticsPanel,
    SearchPanel,
    ParkingMap,
    StreetsPanel
  },
  data() {
    return {
      parkingData: [],
      nearbyResults: [],
      overviewStats: {},
      streetsList: [],
      isLoading: false,
      selectedParkingBay: null,
      selectedStreet: null,

      // Add missing properties for heatmap functionality
      showHeatmap: false,
      displayMode: 'parking' // 'parking', 'heatmap', 'analytics'
    }
  },
  async mounted() {
    await this.loadInitialData()
  },
  methods: {
    async loadInitialData() {
      this.isLoading = true
      try {
        await Promise.all([
          this.loadParkingData(),
          this.loadOverviewStats(),
          this.loadStreetsList()
        ])
      } catch (error) {
        console.error('Error loading initial data:', error)
      } finally {
        this.isLoading = false
      }
    },

    async loadParkingData() {
      try {
        console.log('Loading parking data...')
        const response = await parkingService.getCurrentParkingStatus()
        this.parkingData = response
        console.log(`Loaded ${response.length} parking bays`)
      } catch (error) {
        console.error('Error loading parking data:', error)
        this.parkingData = []
      }
    },

    async loadOverviewStats() {
      try {
        console.log('Loading overview stats...')
        const response = await parkingService.getOverviewStats()
        this.overviewStats = response
        console.log('Overview stats loaded:', response)
      } catch (error) {
        console.error('Error loading overview stats:', error)
        this.overviewStats = {}
      }
    },

    async loadStreetsList() {
      try {
        console.log('Loading streets list...')
        const response = await parkingService.getStreetsList()
        this.streetsList = response
        console.log(`Loaded ${response.length} streets`)
      } catch (error) {
        console.error('Error loading streets list:', error)
        this.streetsList = []
      }
    },

    async handleMapClick(lat, lng) {
      await this.handleFindParking(lat, lng)
    },

    async handleFindParking(lat, lng) {
      this.isLoading = true
      try {
        const response = await parkingService.findNearbyParking(lat, lng, 500)
        this.nearbyResults = response.data || response // 处理两种可能的数据格式
      } catch (error) {
        console.error('Error finding nearby parking:', error)
        this.nearbyResults = []
      } finally {
        this.isLoading = false
      }
    },

    handleSelectBay(bay) {
      this.selectedParkingBay = bay
    },

    handleClearSelection() {
      this.selectedParkingBay = null
    },

    handleSelectStreet(streetName) {
      this.selectedStreet = streetName
      this.selectedParkingBay = null // Clear selected parking bay when changing street
    },

    handleClearStreetFilter() {
      // Use a more robust approach to clear street filter
      try {
        this.selectedStreet = null
        this.selectedParkingBay = null
        this.nearbyResults = []

        // Don't reset display mode - keep current mode (heatmap/parking/analytics)
        // The mode should remain unchanged when clearing street filter

        // Use nextTick to ensure DOM updates are completed before map operations
        this.$nextTick(() => {
          try {
            // Check if parkingMap ref exists and has the required methods
            if (this.$refs.parkingMap && typeof this.$refs.parkingMap.updateDisplay === 'function') {
              this.$refs.parkingMap.updateDisplay()
            }
          } catch (error) {
            console.warn('Error updating map display:', error)
          }
        })
      } catch (error) {
        console.error('Error in handleClearStreetFilter:', error)
      }
    },

    displayAllParkingBays() {
      // Simplified helper method with better error handling
      try {
        if (this.parkingData && this.parkingData.length > 0) {
          console.log(`Displaying all ${this.parkingData.length} parking bays`)

          // Trigger map update if ref exists
          if (this.$refs.parkingMap && typeof this.$refs.parkingMap.updateDisplay === 'function') {
            this.$refs.parkingMap.updateDisplay()
          }
        }
      } catch (error) {
        console.error('Error in displayAllParkingBays:', error)
      }
    },

    async refreshAllData() {
      await this.loadInitialData()
      this.nearbyResults = []
      this.selectedParkingBay = null
      this.selectedStreet = null
    },

    handleToggleHeatmap(enabled) {
      // Handle heatmap toggle from SearchPanel
      console.log(`Heatmap toggled: ${enabled}`)
      this.showHeatmap = enabled
    },

    handleSetDisplayMode(mode) {
      // Handle display mode change from SearchPanel
      console.log(`Display mode set to: ${mode}`)
      this.displayMode = mode
    }
  }
}
</script>

<style scoped>
.parking-website {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  display: flex;
  flex: 1;
  height: calc(100vh - 200px); /* Reserve space for header and other panels */
  gap: 1rem;
  padding: 1rem;
}

.main-content > * {
  flex: 1;
}

/* Ensure proper layout for all panels */
.statistics-panel,
.streets-panel {
  flex-shrink: 0;
}
</style>
