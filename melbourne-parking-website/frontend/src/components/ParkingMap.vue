<template>
  <div id="map" class="map-container" ref="mapContainer"></div>
</template>

<script>
import L from 'leaflet'
import 'leaflet.heat' // Import heatmap plugin

export default {
  name: 'ParkingMap',
  props: {
    parkingData: {
      type: Array,
      default: () => []
    },
    nearbyResults: {
      type: Array,
      default: () => []
    },
    selectedStreet: {
      type: String,
      default: null
    },
    showHeatmap: {
      type: Boolean,
      default: false
    },
    displayMode: {
      type: String,
      default: 'streets' // 'nearest', 'heatmap', 'streets'
    }
  },
  emits: ['mapClick', 'selectParkingBay'],
  data() {
    return {
      map: null,
      markersLayer: null,
      heatmapLayer: null,
      // Custom icons for different parking statuses
      availableIcon: null,
      occupiedIcon: null,
      nearbyIcon: null,
      searchIcon: null,
      // Dynamic icon sizes based on zoom level
      currentZoom: 13,
      baseIconSize: [25, 41],
      // Performance optimization
      zoomUpdateTimer: null,
      lastZoomUpdate: 0,
      iconCache: new Map(),
      // Data caching for performance optimization
      streetDataCache: new Map(), // Cache filtered data by street name
      heatmapDataCache: new Map(), // Cache heatmap data points
      allStreetsDataCache: null, // Cache all streets data
      lastProcessedDataHash: null, // Hash of last processed data to detect changes
      cacheTimestamp: 0, // When cache was last updated
      processingCache: false // Flag to prevent concurrent cache updates
    }
  },
  mounted() {
    this.initializeCustomIcons()
    this.initializeMap()
  },
  watch: {
    parkingData: {
      handler(newData) {
        if (newData && newData.length > 0) {
          this.updateDisplay()
        }
      },
      deep: true
    },
    nearbyResults: {
      handler(newResults) {
        if (this.displayMode === 'nearest') {
          this.displayNearbyResults()
        }
      },
      deep: true
    },
    selectedStreet: {
      handler() {
        if (this.displayMode === 'streets' || this.displayMode === 'parking') {
          this.updateDisplay()
        } else if (this.displayMode === 'heatmap') {
          // Update heatmap when street selection changes in heatmap mode
          this.createHeatmapLayer()
          // Auto-zoom to selected street in heatmap mode
          this.zoomToSelectedStreet()
        }
      }
    },
    displayMode: {
      handler(newMode) {
        this.updateDisplay()
      }
    },
    showHeatmap: {
      handler(newVal) {
        this.toggleHeatmap(newVal)
      }
    }
  },
  methods: {
    // 简化的图标创建，使用固定大小
    initializeCustomIcons() {
      // Create simple, fixed-size icons for better performance
      this.availableIcon = L.icon({
        iconUrl: 'data:image/svg+xml;base64,' + btoa(`
          <svg width="25" height="41" viewBox="0 0 25 41" xmlns="http://www.w3.org/2000/svg">
            <path fill="#27ae60" stroke="#fff" stroke-width="2" d="M12.5 0C5.6 0 0 5.6 0 12.5S12.5 41 12.5 41s12.5-22.9 12.5-35.5S19.4 0 12.5 0z"/>
            <circle fill="#fff" cx="12.5" cy="12.5" r="6"/>
            <text x="12.5" y="17" text-anchor="middle" fill="#27ae60" font-family="Arial" font-size="12" font-weight="bold">P</text>
          </svg>
        `),
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34]
      })

      this.occupiedIcon = L.icon({
        iconUrl: 'data:image/svg+xml;base64,' + btoa(`
          <svg width="25" height="41" viewBox="0 0 25 41" xmlns="http://www.w3.org/2000/svg">
            <path fill="#e74c3c" stroke="#fff" stroke-width="2" d="M12.5 0C5.6 0 0 5.6 0 12.5S12.5 41 12.5 41s12.5-22.9 12.5-35.5S19.4 0 12.5 0z"/>
            <circle fill="#fff" cx="12.5" cy="12.5" r="6"/>
            <text x="12.5" y="17" text-anchor="middle" fill="#e74c3c" font-family="Arial" font-size="12" font-weight="bold">P</text>
          </svg>
        `),
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34]
      })

      this.nearbyIcon = L.icon({
        iconUrl: 'data:image/svg+xml;base64,' + btoa(`
          <svg width="30" height="46" viewBox="0 0 30 46" xmlns="http://www.w3.org/2000/svg">
            <path fill="#00ff00" stroke="#006400" stroke-width="3" d="M15 0C6.7 0 0 6.7 0 15S15 46 15 46s15-24.3 15-31S23.3 0 15 0z"/>
            <circle fill="#fff" cx="15" cy="15" r="8"/>
            <text x="15" y="20" text-anchor="middle" fill="#00ff00" font-family="Arial" font-size="14" font-weight="bold">P</text>
          </svg>
        `),
        iconSize: [30, 46],
        iconAnchor: [15, 46],
        popupAnchor: [1, -40]
      })

      this.searchIcon = L.icon({
        iconUrl: 'data:image/svg+xml;base64,' + btoa(`
          <svg width="35" height="51" viewBox="0 0 35 51" xmlns="http://www.w3.org/2000/svg">
            <path fill="#3498db" stroke="#fff" stroke-width="3" d="M17.5 0C7.8 0 0 7.8 0 17.5S17.5 51 17.5 51s17.5-25.7 17.5-33.5S27.2 0 17.5 0z"/>
            <circle fill="#fff" cx="17.5" cy="17.5" r="10"/>
            <circle fill="#3498db" cx="17.5" cy="17.5" r="6"/>
          </svg>
        `),
        iconSize: [35, 51],
        iconAnchor: [17, 51],
        popupAnchor: [1, -46]
      })
    },

    initializeMap() {
      // Initialize Leaflet map centered on Melbourne CBD
      this.map = L.map(this.$refs.mapContainer).setView([-37.8136, 144.9631], 13)

      // Add OpenStreetMap tiles
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(this.map)

      // Initialize markers layer
      this.markersLayer = L.layerGroup().addTo(this.map)

      // Add click event to find nearby parking
      this.map.on('click', (e) => {
        this.$emit('mapClick', e.latlng.lat, e.latlng.lng)
      })

      // 移除复杂的缩放监听，恢复单高性能的地图
      // 不再监听zoomend事件，避免性能问题
    },

    updateIconSizes(zoomLevel) {
      // Update icon sizes based on zoom level
      const newSize = Math.max(20, 25 - (zoomLevel - 13) * 2)

      this.availableIcon.options.iconSize = [newSize, newSize * 1.64]
      this.occupiedIcon.options.iconSize = [newSize, newSize * 1.64]
      this.nearbyIcon.options.iconSize = [newSize * 1.2, newSize * 1.2 * 1.53]
      this.searchIcon.options.iconSize = [newSize * 1.4, newSize * 1.4 * 1.46]

      // Redraw markers with new icon sizes
      this.displayParkingBays()
      this.displayNearbyResults()
    },

    // Update display based on current mode
    updateDisplay() {
      if (!this.map) return

      // Ensure data is cached before displaying
      this.ensureDataCached()

      // Clear all layers first
      this.clearAllLayers()

      switch (this.displayMode) {
        case 'heatmap':
          this.toggleHeatmap(true)
          break
        case 'parking':
        case 'streets': // Keep backward compatibility
          if (this.parkingData && this.parkingData.length > 0) {
            this.displayParkingBays()
          }
          break
      }
    },

    // Data Caching Methods for Performance Optimization
    ensureDataCached() {
      if (!this.parkingData || this.parkingData.length === 0) return

      // Generate hash of current data to check if it has changed
      const currentDataHash = this.generateDataHash(this.parkingData)

      // Only rebuild cache if data has changed
      if (this.lastProcessedDataHash !== currentDataHash && !this.processingCache) {
        this.processingCache = true
        console.log('🔄 Rebuilding data cache...')
        this.preprocessParkingData()
        this.lastProcessedDataHash = currentDataHash
        this.cacheTimestamp = Date.now()
        this.processingCache = false
        console.log('✅ Data cache updated')
      }
    },

    generateDataHash(data) {
      // Simple hash function for detecting data changes
      return data.length + '-' + (data[0]?.kerbside_id || '') + '-' + (data[data.length - 1]?.kerbside_id || '')
    },

    preprocessParkingData() {
      if (!this.parkingData || this.parkingData.length === 0) return

      // Clear existing caches
      this.streetDataCache.clear()
      this.heatmapDataCache.clear()

      // Cache all streets data (for when no street is selected)
      this.allStreetsDataCache = [...this.parkingData]

      // Group data by street for faster filtering
      const streetGroups = {}

      this.parkingData.forEach(bay => {
        const streetName = bay.road_segment
        if (!streetName) return

        if (!streetGroups[streetName]) {
          streetGroups[streetName] = []
        }
        streetGroups[streetName].push(bay)
      })

      // Cache filtered data for each street
      Object.keys(streetGroups).forEach(streetName => {
        this.streetDataCache.set(streetName, streetGroups[streetName])

        // Pre-calculate heatmap data for this street
        const heatmapData = streetGroups[streetName].map(bay => [
          bay.latitude,
          bay.longitude,
          bay.status === 'Unoccupied' ? 0.8 : 0.2
        ])
        this.heatmapDataCache.set(streetName, heatmapData)
      })

      // Cache heatmap data for all streets
      const allHeatmapData = this.parkingData.map(bay => [
        bay.latitude,
        bay.longitude,
        bay.status === 'Unoccupied' ? 0.8 : 0.2
      ])
      this.heatmapDataCache.set('__ALL_STREETS__', allHeatmapData)

      console.log(`📊 Cached data for ${Object.keys(streetGroups).length} streets`)
    },

    getCachedStreetData(streetName) {
      if (!streetName) {
        return this.allStreetsDataCache || this.parkingData
      }

      return this.streetDataCache.get(streetName) || []
    },

    getCachedHeatmapData(streetName) {
      const cacheKey = streetName || '__ALL_STREETS__'
      return this.heatmapDataCache.get(cacheKey) || []
    },

    invalidateCache() {
      this.streetDataCache.clear()
      this.heatmapDataCache.clear()
      this.allStreetsDataCache = null
      this.lastProcessedDataHash = null
      console.log('🗑️ Cache invalidated')
    },

    clearAllLayers() {
      // Clear markers layer
      if (this.markersLayer) {
        this.markersLayer.clearLayers()
      }

      // Clear heatmap layer
      if (this.heatmapLayer) {
        this.map.removeLayer(this.heatmapLayer)
        this.heatmapLayer = null
      }
    },

    displayParkingBays() {
      // Only display parking bays if not in heatmap mode
      if (this.displayMode === 'heatmap') return

      if (!this.map || !this.parkingData) return

      // Clear existing markers
      this.markersLayer.clearLayers()

      // Use cached data instead of filtering every time
      const filteredParkingData = this.getCachedStreetData(this.selectedStreet)

      console.log(`🚀 Using cached data: ${filteredParkingData.length} parking bays for ${this.selectedStreet || 'all streets'}`)

      // Add parking bay pin markers
      filteredParkingData.forEach(bay => {
        const isAvailable = bay.status === 'Unoccupied'
        const icon = isAvailable ? this.availableIcon : this.occupiedIcon

        const marker = L.marker([bay.latitude, bay.longitude], {
          icon: icon
        })

        // Add click event to marker to emit parking bay selection
        marker.on('click', () => {
          this.$emit('selectParkingBay', bay)
        })

        // Keep popup for additional information
        marker.bindPopup(`
          <div class="parking-popup">
            <h4>🅿️ Parking Bay ${bay.kerbside_id}</h4>
            <div class="popup-status">
              <span class="status-badge ${isAvailable ? 'available' : 'occupied'}">
                ${isAvailable ? '✅ Available' : '❌ Occupied'}
              </span>
            </div>
            <p><strong>📍 Location:</strong> ${bay.road_segment || 'Unknown'}</p>
            <p><strong>🏢 Zone:</strong> ${bay.zone_number || 'N/A'}</p>
          </div>
        `)

        this.markersLayer.addLayer(marker)
      })

      // Fit map to show filtered parking bays or reset to default view
      if (filteredParkingData.length > 0) {
        if (this.selectedStreet) {
          // When street is selected, focus on that street's parking bays
          const group = new L.featureGroup(this.markersLayer.getLayers())
          if (group.getLayers().length > 0) {
            this.map.fitBounds(group.getBounds().pad(0.1))
          }
        } else {
          // When showing all streets, reset to Melbourne CBD overview
          this.map.setView([-37.8136, 144.9631], 13)
        }
      }
    },

    displayNearbyResults() {
      // Only display nearby results if in nearest mode
      if (this.displayMode !== 'nearest') return

      if (!this.map || !this.nearbyResults || this.nearbyResults.length === 0) return

      // Clear existing markers and add new ones
      this.markersLayer.clearLayers()

      // Display search location marker
      if (this.nearbyResults.length > 0) {
        const searchLat = this.nearbyResults[0].search_lat
        const searchLng = this.nearbyResults[0].search_lng

        if (searchLat && searchLng) {
          const searchMarker = L.marker([searchLat, searchLng], {
            icon: this.searchIcon
          }).bindPopup(`
            <div class="parking-popup">
              <h4>📍 Search Location</h4>
              <p>Looking for parking near here</p>
            </div>
          `)
          searchMarker.addTo(this.markersLayer)
        }
      }

      // Add nearby parking bay markers
      this.nearbyResults.forEach(result => {
        const isAvailable = result.status === 'Unoccupied'
        const icon = isAvailable ? this.nearbyIcon : this.occupiedIcon

        const marker = L.marker([result.latitude, result.longitude], {
          icon: icon
        })

        marker.on('click', () => {
          this.$emit('selectParkingBay', result)
        })

        marker.bindPopup(`
          <div class="parking-popup">
            <h4>����️ Nearby Parking Bay ${result.kerbside_id}</h4>
            <div class="popup-status">
              <span class="status-badge ${isAvailable ? 'available' : 'occupied'}">
                ${isAvailable ? '✅ Available' : '❌ Occupied'}
              </span>
            </div>
            <p><strong>📍 Distance:</strong> ${result.distance ? result.distance.toFixed(0) + 'm' : 'N/A'}</p>
            <p><strong>🛣️ Street:</strong> ${result.road_segment || 'Unknown'}</p>
            <p><strong>🏢 Zone:</strong> ${result.zone_number || 'N/A'}</p>
          </div>
        `)

        marker.addTo(this.markersLayer)
      })

      // Center map on search results
      if (this.nearbyResults.length > 0) {
        const group = new L.featureGroup(this.markersLayer.getLayers())
        if (group.getLayers().length > 0) {
          this.map.fitBounds(group.getBounds().pad(0.1))
        }
      }
    },

    clearMarkers() {
      if (this.markersLayer) {
        this.markersLayer.clearLayers()
      }
    },

    focusOnLocation(lat, lng, zoom = 16) {
      if (this.map) {
        this.map.setView([lat, lng], zoom)
      }
    },

    // Heatmap functionality methods
    toggleHeatmap(showHeatmap) {
      if (showHeatmap && this.parkingData && this.parkingData.length > 0) {
        this.createHeatmapLayer()
        this.clearMarkers()
        this.addHeatmapClickHandlers()
      } else {
        this.removeHeatmapLayer()
        this.displayParkingBays()
      }
    },

    addHeatmapClickHandlers() {
      // Get filtered data for click detection
      let filteredData
      if (this.selectedStreet) {
        filteredData = this.getCachedStreetData(this.selectedStreet)
      } else {
        filteredData = this.parkingData || []
      }

      if (!filteredData || filteredData.length === 0) return

      // Add invisible markers for click detection in heatmap mode
      filteredData.forEach(bay => {
        // Create invisible marker for click detection
        const invisibleIcon = L.divIcon({
          className: 'invisible-marker',
          iconSize: [20, 20],
          iconAnchor: [10, 10]
        })

        const marker = L.marker([bay.latitude, bay.longitude], {
          icon: invisibleIcon,
          opacity: 0 // Make marker invisible
        })

        // Add click event to show parking bay info
        marker.on('click', () => {
          this.$emit('selectParkingBay', bay)

          // Show popup with parking bay information
          const isAvailable = bay.status === 'Unoccupied'
          const popupContent = `
            <div class="heatmap-popup">
              <h4>🅿️ Parking Bay ${bay.kerbside_id}</h4>
              <div class="popup-status">
                <span class="status-badge ${isAvailable ? 'available' : 'occupied'}">
                  ${isAvailable ? '✅ Available' : '❌ Occupied'}
                </span>
              </div>
              <p><strong>📍 Location:</strong> ${bay.road_segment || 'Unknown'}</p>
              <p><strong>🏢 Zone:</strong> ${bay.zone_number || 'N/A'}</p>
            </div>
          `

          marker.bindPopup(popupContent).openPopup()
        })

        // Add marker to the map for click detection
        this.markersLayer.addLayer(marker)
      })

      console.log(`Added ${filteredData.length} invisible markers for heatmap click detection`)
    },

    createHeatmapLayer() {
      // Remove existing heatmap layer if it exists
      this.removeHeatmapLayer()

      // Get filtered data - use cached data if available, otherwise use direct filtering
      let filteredData
      if (this.selectedStreet) {
        filteredData = this.getCachedStreetData(this.selectedStreet)
      } else {
        filteredData = this.parkingData || []
      }

      if (!filteredData || filteredData.length === 0) {
        console.warn('No data available for heatmap')
        return
      }

      // Create heatmap data points
      // Weight: Available spots get higher weight (more intense on heatmap)
      const heatmapPoints = filteredData.map(bay => [
        bay.latitude,
        bay.longitude,
        bay.status === 'Unoccupied' ? 0.8 : 0.2 // Available spots are "hotter" (more desirable)
      ])

      console.log(`Creating heatmap with ${heatmapPoints.length} data points`)

      // Create heatmap layer with custom options
      this.heatmapLayer = L.heatLayer(heatmapPoints, {
        radius: 25,
        blur: 15,
        maxZoom: 17,
        max: 1.0,
        gradient: {
          0.0: '#313695',  // Cold (occupied/less available) - dark blue
          0.2: '#4575b4',  // Cool blue
          0.4: '#74add1',  // Light blue
          0.6: '#abd9e9',  // Very light blue
          0.7: '#e0f3f8',  // Almost white
          0.8: '#fee090',  // Light yellow (available spots)
          0.9: '#fdae61',  // Orange
          1.0: '#f46d43'   // Hot (most available) - red-orange
        }
      })

      // Add heatmap layer to map
      this.heatmapLayer.addTo(this.map)

      console.log('Heatmap layer created and added to map')
    },

    removeHeatmapLayer() {
      if (this.heatmapLayer) {
        this.map.removeLayer(this.heatmapLayer)
        this.heatmapLayer = null
        console.log('Heatmap layer removed')
      }
    },

    // Auto-zoom functionality for heatmap mode
    zoomToSelectedStreet() {
      if (!this.map) return

      if (this.selectedStreet) {
        // Get filtered data for the selected street
        const streetData = this.getCachedStreetData(this.selectedStreet)

        if (streetData && streetData.length > 0) {
          console.log(`Zooming to street: ${this.selectedStreet} (${streetData.length} parking bays)`)

          // Create temporary markers to calculate bounds
          const tempMarkers = streetData.map(bay =>
            L.marker([bay.latitude, bay.longitude])
          )

          // Create feature group to get bounds
          const group = new L.featureGroup(tempMarkers)

          // Fit map to street bounds with appropriate zoom
          this.map.fitBounds(group.getBounds(), {
            padding: [20, 20], // Add padding around the bounds
            maxZoom: 16 // Limit maximum zoom level for better overview
          })

          console.log(`✅ Zoomed to street: ${this.selectedStreet}`)
        } else {
          console.warn(`No data found for street: ${this.selectedStreet}`)
        }
      } else {
        // Show entire Melbourne CBD when no street is selected
        console.log('Showing entire Melbourne CBD heatmap')

        // Calculate bounds for all parking data to show complete coverage
        const allData = this.parkingData || []
        if (allData.length > 0) {
          // Create temporary markers from all parking data
          const allMarkers = allData.map(bay =>
            L.marker([bay.latitude, bay.longitude])
          )

          // Create feature group to calculate bounds of all data
          const allGroup = new L.featureGroup(allMarkers)

          // Fit map to show all parking data with some padding
          this.map.fitBounds(allGroup.getBounds(), {
            padding: [30, 30], // More padding for better overview
            maxZoom: 14 // Slightly zoomed out to show entire CBD area
          })

          console.log(`✅ Displaying entire Melbourne CBD with ${allData.length} parking spots`)
        } else {
          // Fallback to default Melbourne CBD center if no data
          console.log('Using default Melbourne CBD view')
          this.map.setView([-37.8136, 144.9631], 13)
        }
      }
    },

    clearAllLayers() {
      this.clearMarkers()
      this.removeHeatmapLayer()
    },
  },

  beforeUnmount() {
    if (this.map) {
      this.map.remove()
    }
  }
}
</script>

<style scoped>
.map-container {
  height: 100%;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Parking popup styles */
:deep(.parking-popup) {
  min-width: 250px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

:deep(.parking-popup h4) {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 16px;
  border-bottom: 2px solid #ecf0f1;
  padding-bottom: 5px;
}

:deep(.popup-status) {
  margin: 10px 0;
  text-align: center;
}

:deep(.status-badge) {
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 13px;
  display: inline-block;
}

:deep(.status-badge.available) {
  background-color: #d5f4e6;
  color: #27ae60;
  border: 1px solid #27ae60;
}

:deep(.status-badge.occupied) {
  background-color: #fdeaea;
  color: #e74c3c;
  border: 1px solid #e74c3c;
}

:deep(.parking-popup p) {
  margin: 8px 0;
  color: #34495e;
  font-size: 13px;
}

:deep(.parking-popup strong) {
  color: #2c3e50;
}

/* Map controls styling */
:deep(.leaflet-control-zoom) {
  border-radius: 8px !important;
  border: none !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
}

:deep(.leaflet-control-zoom a) {
  background-color: #fff !important;
  border: none !important;
  color: #2c3e50 !important;
  font-weight: bold !important;
}

:deep(.leaflet-control-zoom a:hover) {
  background-color: #3498db !important;
  color: white !important;
}

/* Hide invisible markers used for heatmap click detection */
:deep(.invisible-marker) {
  background: transparent !important;
  border: none !important;
}

/* Heatmap popup styling */
:deep(.heatmap-popup) {
  min-width: 250px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(5px);
}

:deep(.heatmap-popup h4) {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 16px;
  border-bottom: 2px solid #ecf0f1;
  padding-bottom: 5px;
}
</style>
