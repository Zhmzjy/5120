<!--
Advanced Analytics Component for Melbourne Parking Website
Contains population data analysis and historical trend analysis
-->
<template>
  <div class="analytics-panel">
    <h3>Advanced Analytics</h3>

    <!-- Analysis Mode Selection -->
    <div class="analysis-mode-selection">
      <button
        @click="setAnalysisMode('population')"
        :class="['analysis-btn', { active: analysisMode === 'population' }]"
      >
        Population Analysis
      </button>
      <button
        @click="setAnalysisMode('historical')"
        :class="['analysis-btn', { active: analysisMode === 'historical' }]"
      >
        Historical Trends
      </button>
    </div>

    <!-- Analysis Content -->
    <div class="analysis-content">
      <!-- Population Data Analysis -->
      <div v-if="analysisMode === 'population'" class="analysis-section">
        <div class="section-description">
          <p>Analyze population growth trends and their correlation with parking demand</p>
        </div>

        <div class="chart-container">
          <canvas ref="populationChart" id="population-chart"></canvas>
        </div>

        <div v-if="populationData.length > 0" class="analysis-summary">
          <h5>Victoria Population Growth Summary</h5>
          <div class="summary-stats">
            <div class="stat-item">
              <span class="stat-label">Latest Growth Rate:</span>
              <span class="stat-value">{{ latestGrowthRate }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Total Growth 2016-2021:</span>
              <span class="stat-value">{{ totalPopulationGrowth.toLocaleString() }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Average Annual Growth:</span>
              <span class="stat-value">{{ averageAnnualGrowth }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Historical Trends Analysis -->
      <div v-if="analysisMode === 'historical'" class="analysis-section">
        <div class="section-description">
          <p>Historical parking usage patterns and trends analysis</p>
        </div>

        <!-- Time Period Selection -->
        <div class="time-period-selector">
          <label>Analysis Period:</label>
          <select v-model="selectedPeriod" @change="loadHistoricalData">
            <option value="7d">Last 7 Days</option>
            <option value="1m">Last Month</option>
            <option value="3m">Last 3 Months</option>
          </select>
        </div>

        <div class="chart-container">
          <canvas ref="historicalChart" id="historical-chart"></canvas>
        </div>

        <div v-if="historicalData.length > 0" class="analysis-summary">
          <h5>Historical Trends Summary</h5>
          <div class="summary-stats">
            <div class="stat-item">
              <span class="stat-label">Peak Usage Time:</span>
              <span class="stat-value">{{ peakUsageTime }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Average Occupancy:</span>
              <span class="stat-value">{{ averageOccupancy }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Trend Direction:</span>
              <span class="stat-value" :class="trendDirection.class">{{ trendDirection.text }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading analysis data...</p>
      </div>

      <!-- Error State -->
      <div v-if="error" class="error-state">
        <p>{{ error }}</p>
        <button @click="retryAnalysis" class="retry-btn">Retry</button>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
import analyticsService from '../services/analyticsService.js'

Chart.register(...registerables)

export default {
  name: 'AdvancedAnalytics',
  props: {
    parkingData: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      analysisMode: 'population', // 'population' or 'historical'
      selectedPeriod: '1m',
      isLoading: false,
      error: null,

      // Population data
      populationData: [],
      populationChart: null,

      // Historical data
      historicalData: [],
      historicalChart: null,

      // Analysis results
      latestGrowthRate: '0.0',
      totalPopulationGrowth: 0,
      averageAnnualGrowth: '0.0',
      peakUsageTime: 'N/A',
      averageOccupancy: '0.0',
      trendDirection: { text: 'Stable', class: 'stable' }
    }
  },
  mounted() {
    this.initializeAnalysis()
  },
  beforeUnmount() {
    this.destroyCharts()
  },
  watch: {
    analysisMode: {
      handler(newMode) {
        this.handleModeChange(newMode)
      }
    },
    parkingData: {
      handler() {
        if (this.analysisMode === 'historical') {
          this.loadHistoricalData()
        }
      },
      deep: true
    }
  },
  methods: {
    async initializeAnalysis() {
      await this.loadPopulationData()
      this.handleModeChange(this.analysisMode)
    },

    setAnalysisMode(mode) {
      this.analysisMode = mode
    },

    handleModeChange(mode) {
      this.destroyCharts()
      this.error = null

      this.$nextTick(() => {
        if (mode === 'population') {
          this.createPopulationChart()
        } else if (mode === 'historical') {
          this.loadHistoricalData()
        }
      })
    },

    async loadPopulationData() {
      this.isLoading = true
      this.error = null

      try {
        console.log('Loading population data...')
        const data = await analyticsService.getPopulationData()
        this.populationData = data
        this.calculatePopulationStats()
        console.log('Population data loaded:', data)
      } catch (error) {
        console.error('Error loading population data:', error)
        this.error = 'Failed to load population data. Please try again.'
        // Use mock data as fallback
        this.populationData = this.getMockPopulationData()
        this.calculatePopulationStats()
      } finally {
        this.isLoading = false
      }
    },

    async loadHistoricalData() {
      if (this.analysisMode !== 'historical') return

      this.isLoading = true
      this.error = null

      try {
        console.log(`Loading historical data for period: ${this.selectedPeriod}`)
        const data = await analyticsService.getHistoricalData(this.selectedPeriod)
        this.historicalData = data
        this.calculateHistoricalStats()
        this.createHistoricalChart()
        console.log('Historical data loaded:', data)
      } catch (error) {
        console.error('Error loading historical data:', error)
        this.error = 'Failed to load historical data. Please try again.'
        // Use mock data as fallback
        this.historicalData = this.getMockHistoricalData()
        this.calculateHistoricalStats()
        this.createHistoricalChart()
      } finally {
        this.isLoading = false
      }
    },

    createPopulationChart() {
      if (!this.$refs.populationChart || this.populationData.length === 0) return

      const ctx = this.$refs.populationChart.getContext('2d')

      // Extract Victoria data for chart
      const victoriaData = this.populationData.find(item => item.state === 'Vic.')
      if (!victoriaData || !victoriaData.growthNumbers || !victoriaData.growthRates) {
        console.warn('Victoria data not found or incomplete')
        return
      }

      // Destroy existing chart if it exists
      if (this.populationChart) {
        this.populationChart.destroy()
      }

      this.populationChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['2016-2017', '2017-2018', '2018-2019', '2019-2020', '2020-2021'],
          datasets: [{
            label: 'Victoria Population Growth',
            data: victoriaData.growthNumbers || [],
            borderColor: '#3498db',
            backgroundColor: 'rgba(52, 152, 219, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#3498db',
            pointBorderColor: '#2980b9',
            pointBorderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: 'Victoria Population Growth (2016-2021)',
              font: {
                size: 16,
                weight: 'bold'
              },
              color: '#2c3e50'
            },
            legend: {
              display: true,
              position: 'top'
            },
            tooltip: {
              mode: 'index',
              intersect: false,
              callbacks: {
                label: function(context) {
                  const value = context.parsed.y
                  const percentage = victoriaData.growthRates[context.dataIndex] || '0.0'
                  return `Growth: ${value?.toLocaleString() || 'N/A'} people (${percentage}%)`
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: false,
              title: {
                display: true,
                text: 'Population Growth (Number of People)',
                color: '#7f8c8d'
              },
              ticks: {
                callback: function(value) {
                  return value?.toLocaleString() || '0'
                }
              }
            },
            x: {
              title: {
                display: true,
                text: 'Year Period',
                color: '#7f8c8d'
              }
            }
          },
          interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
          }
        }
      })
    },

    createHistoricalChart() {
      if (!this.$refs.historicalChart || this.historicalData.length === 0) return

      const ctx = this.$refs.historicalChart.getContext('2d')

      // Destroy existing chart if it exists
      if (this.historicalChart) {
        this.historicalChart.destroy()
      }

      this.historicalChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.historicalData.map(item => item.period || 'N/A'),
          datasets: [{
            label: 'Occupancy Rate (%)',
            data: this.historicalData.map(item => item.occupancyRate || 0),
            borderColor: '#e74c3c',
            backgroundColor: 'rgba(231, 76, 60, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#e74c3c',
            pointBorderColor: '#c0392b',
            pointBorderWidth: 2,
            pointRadius: 5,
            pointHoverRadius: 7,
            yAxisID: 'y'
          }, {
            label: 'Available Spots',
            data: this.historicalData.map(item => Math.round(item.availableSpots || 0)),
            borderColor: '#27ae60',
            backgroundColor: 'rgba(39, 174, 96, 0.1)',
            borderWidth: 3,
            fill: false,
            tension: 0.4,
            pointBackgroundColor: '#27ae60',
            pointBorderColor: '#229954',
            pointBorderWidth: 2,
            pointRadius: 5,
            pointHoverRadius: 7,
            yAxisID: 'y1'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: true,
              text: `Parking Usage Trends - ${this.getPeriodText()}`,
              font: {
                size: 16,
                weight: 'bold'
              },
              color: '#2c3e50'
            },
            legend: {
              display: true,
              position: 'top'
            },
            tooltip: {
              mode: 'index',
              intersect: false,
              callbacks: {
                label: function(context) {
                  const value = context.parsed.y
                  if (context.datasetIndex === 0) {
                    return `Occupancy: ${value?.toFixed(1) || '0.0'}%`
                  } else {
                    return `Available: ${Math.round(value) || 0} spots`
                  }
                }
              }
            }
          },
          scales: {
            y: {
              type: 'linear',
              display: true,
              position: 'left',
              title: {
                display: true,
                text: 'Occupancy Rate (%)',
                color: '#7f8c8d'
              },
              min: 0,
              max: 100,
              ticks: {
                callback: function(value) {
                  return value + '%'
                }
              }
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              title: {
                display: true,
                text: 'Available Spots',
                color: '#7f8c8d'
              },
              grid: {
                drawOnChartArea: false,
              },
              ticks: {
                callback: function(value) {
                  return Math.round(value)
                }
              }
            },
            x: {
              title: {
                display: true,
                text: 'Time Period',
                color: '#7f8c8d'
              }
            }
          },
          interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
          }
        }
      })
    },

    calculatePopulationStats() {
      if (this.populationData.length === 0) return

      const victoriaData = this.populationData.find(item => item.state === 'Vic.')
      if (!victoriaData) return

      // Calculate latest growth rate
      const growthRates = victoriaData.growthRates
      this.latestGrowthRate = growthRates[growthRates.length - 1]

      // Calculate total growth
      this.totalPopulationGrowth = victoriaData.growthNumbers.reduce((sum, num) => sum + num, 0)

      // Calculate average annual growth
      const averageGrowth = growthRates.reduce((sum, rate) => sum + parseFloat(rate), 0) / growthRates.length
      this.averageAnnualGrowth = averageGrowth.toFixed(1)
    },

    calculateHistoricalStats() {
      if (this.historicalData.length === 0) return

      // Find peak usage time
      const peakData = this.historicalData.reduce((peak, current) =>
        current.occupancyRate > peak.occupancyRate ? current : peak
      )
      this.peakUsageTime = peakData.period

      // Calculate average occupancy
      const totalOccupancy = this.historicalData.reduce((sum, item) => sum + item.occupancyRate, 0)
      this.averageOccupancy = (totalOccupancy / this.historicalData.length).toFixed(1)

      // Determine trend direction
      const firstRate = this.historicalData[0].occupancyRate
      const lastRate = this.historicalData[this.historicalData.length - 1].occupancyRate
      const difference = lastRate - firstRate

      if (difference > 5) {
        this.trendDirection = { text: 'Increasing', class: 'increasing' }
      } else if (difference < -5) {
        this.trendDirection = { text: 'Decreasing', class: 'decreasing' }
      } else {
        this.trendDirection = { text: 'Stable', class: 'stable' }
      }
    },

    destroyCharts() {
      if (this.populationChart) {
        this.populationChart.destroy()
        this.populationChart = null
      }
      if (this.historicalChart) {
        this.historicalChart.destroy()
        this.historicalChart = null
      }
    },

    retryAnalysis() {
      if (this.analysisMode === 'population') {
        this.loadPopulationData()
      } else {
        this.loadHistoricalData()
      }
    },

    getPeriodText() {
      const periods = {
        '7d': 'Last 7 Days',
        '1m': 'Last Month',
        '3m': 'Last 3 Months'
      }
      return periods[this.selectedPeriod] || 'Unknown Period'
    },

    // Mock data for fallback
    getMockPopulationData() {
      return [{
        state: 'Vic.',
        growthNumbers: [209495, 214408, 236429, 215728, 188855],
        growthRates: ['4.2', '4.2', '4.5', '4.0', '3.5']
      }]
    },

    getMockHistoricalData() {
      const mockData = []
      const periods = this.selectedPeriod === '7d' ? 7 : this.selectedPeriod === '1m' ? 30 : 90

      for (let i = 0; i < Math.min(periods, 20); i++) {
        const date = new Date()
        date.setDate(date.getDate() - i)

        mockData.unshift({
          period: date.toLocaleDateString(),
          occupancyRate: 60 + Math.sin(i * 0.2) * 20 + Math.random() * 10,
          availableSpots: 1200 + Math.cos(i * 0.3) * 400 + Math.random() * 200
        })
      }

      return mockData
    }
  }
}
</script>

<style scoped>
.analytics-panel {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin: 1rem 0;
}

.analytics-panel h3 {
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
  font-size: 1.2rem;
  border-bottom: 2px solid #ecf0f1;
  padding-bottom: 0.5rem;
}

/* Analysis Mode Selection */
.analysis-mode-selection {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.analysis-btn {
  background-color: #ecf0f1;
  color: #2c3e50;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  min-width: 140px;
}

.analysis-btn:hover {
  background-color: #d5dbdb;
  transform: translateY(-1px);
}

.analysis-btn.active {
  background-color: #3498db;
  color: white;
  box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3);
}

/* Analysis Content */
.analysis-content {
  min-height: 400px;
}

.analysis-section {
  animation: fadeIn 0.3s ease-in-out;
}

.section-description {
  margin-bottom: 1rem;
}

.section-description p {
  color: #7f8c8d;
  font-size: 0.95rem;
  line-height: 1.4;
  margin: 0;
}

/* Chart Container */
.chart-container {
  position: relative;
  height: 300px;
  margin: 1.5rem 0;
  background-color: #fafbfc;
  border-radius: 6px;
  padding: 1rem;
  border: 1px solid #e1e8ed;
}

#population-chart, #historical-chart {
  width: 100% !important;
  height: 100% !important;
}

/* Time Period Selector */
.time-period-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.time-period-selector label {
  color: #2c3e50;
  font-weight: 500;
  font-size: 0.9rem;
}

.time-period-selector select {
  padding: 0.4rem 0.8rem;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #2c3e50;
  background-color: white;
}

/* Analysis Summary */
.analysis-summary {
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 1rem;
  margin-top: 1.5rem;
  border-left: 4px solid #3498db;
}

.analysis-summary h5 {
  color: #2c3e50;
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.summary-stats {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.8rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #ecf0f1;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.9rem;
  font-weight: 500;
}

.stat-value {
  color: #2c3e50;
  font-size: 0.9rem;
  font-weight: 600;
}

.stat-value.increasing {
  color: #e74c3c;
}

.stat-value.decreasing {
  color: #27ae60;
}

.stat-value.stable {
  color: #f39c12;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  gap: 1rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #ecf0f1;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-state p {
  color: #7f8c8d;
  margin: 0;
}

/* Error State */
.error-state {
  text-align: center;
  padding: 2rem;
  color: #e74c3c;
}

.retry-btn {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 0.5rem;
}

.retry-btn:hover {
  background-color: #c0392b;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .analysis-mode-selection {
    flex-direction: column;
  }

  .analysis-btn {
    min-width: auto;
  }

  .summary-stats {
    grid-template-columns: 1fr;
  }

  .stat-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.2rem;
  }
}
</style>
