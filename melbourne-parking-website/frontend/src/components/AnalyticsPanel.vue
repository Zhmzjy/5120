<!--
Compact Analytics Panel Component for Smart Parking Search
Provides population and historical trend analysis in a compact format
-->
<template>
  <div class="analytics-panel">
    <!-- Analysis Type Selection -->
    <div class="analysis-type-selection">
      <button
        @click="setAnalysisType('population')"
        :class="['analysis-btn', { active: analysisType === 'population' }]"
      >
        Population Data
      </button>
      <button
        @click="setAnalysisType('historical')"
        :class="['analysis-btn', { active: analysisType === 'historical' }]"
      >
        Historical Trends
      </button>
    </div>

    <!-- Population Analysis -->
    <div v-if="analysisType === 'population'" class="analysis-content">
      <div class="chart-container" ref="populationChartContainer">
        <!-- Dynamic canvas creation to avoid stale references -->
        <canvas :id="'population-chart-' + canvasKey"></canvas>
      </div>

      <div v-if="populationData.length > 0" class="analysis-summary">
        <div class="stat-item">
          <span class="stat-label">Latest Growth:</span>
          <span class="stat-value">{{ latestGrowthRate }}%</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">5-Year Growth:</span>
          <span class="stat-value">{{ totalPopulationGrowth.toLocaleString() }}</span>
        </div>
      </div>
    </div>

    <!-- Historical Trends Analysis -->
    <div v-if="analysisType === 'historical'" class="analysis-content">
      <div class="time-period-selector">
        <select v-model="selectedPeriod" @change="loadHistoricalData">
          <option value="7d">Last 7 Days</option>
          <option value="1m">Last Month</option>
          <option value="3m">Last 3 Months</option>
        </select>
      </div>

      <div class="chart-container" ref="historicalChartContainer">
        <!-- Dynamic canvas creation to avoid stale references -->
        <canvas :id="'historical-chart-' + canvasKey"></canvas>
      </div>

      <div v-if="historicalData.length > 0" class="analysis-summary">
        <div class="stat-item">
          <span class="stat-label">Peak Usage:</span>
          <span class="stat-value">{{ peakUsageTime }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Avg. Occupancy:</span>
          <span class="stat-value">{{ averageOccupancy }}%</span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading data...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="retryAnalysis" class="retry-btn">Retry</button>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
import analyticsService from '../services/analyticsService.js'

Chart.register(...registerables)

export default {
  name: 'AnalyticsPanel',
  props: {
    parkingData: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      analysisType: 'population',
      selectedPeriod: '7d',
      isLoading: false,
      error: null,

      // Unique key for canvas elements to force re-render
      canvasKey: 0,

      // Chart instances
      populationChart: null,
      historicalChart: null,

      // Data
      populationData: [],
      historicalData: [],

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
    this.destroyAllCharts()
  },
  methods: {
    async initializeAnalysis() {
      await this.loadPopulationData()
      // 直接创建当前类型的图表
      this.createCurrentChart()
    },

    setAnalysisType(type) {
      if (this.analysisType === type) return

      console.log(`Switching analysis type to: ${type}`)

      // 先销毁所有现有图表
      this.destroyAllCharts()

      // 更新分析类型
      this.analysisType = type

      // 清除任何待处理的错误
      this.error = null

      // 重新生成 canvas key 以强制 DOM 更新
      this.canvasKey++

      // 等待 DOM 更新后创建新图表
      this.$nextTick(() => {
        // 再次确保图表被完全销毁
        this.destroyAllCharts()

        // 根据类型加载数据和创建图表
        if (type === 'population') {
          if (this.populationData.length > 0) {
            // 延迟创建以确保DOM准备就绪
            setTimeout(() => {
              this.createPopulationChart()
            }, 100)
          } else {
            this.loadPopulationData()
          }
        } else if (type === 'historical') {
          this.loadHistoricalData()
        }
      })
    },

    createCurrentChart() {
      // 确保之前的图表已被完全销毁
      this.destroyAllCharts()

      this.$nextTick(() => {
        if (this.analysisType === 'population' && this.populationData.length > 0) {
          setTimeout(() => {
            this.createPopulationChart()
          }, 100)
        } else if (this.analysisType === 'historical' && this.historicalData.length > 0) {
          setTimeout(() => {
            this.createHistoricalChart()
          }, 100)
        }
      })
    },

    async loadPopulationData() {
      if (this.isLoading) return // 防止重复加载

      this.isLoading = true
      this.error = null

      try {
        const data = await analyticsService.getPopulationData()
        this.populationData = data
        this.calculatePopulationStats()

        // 只有当前是人口分析模式时才创建图表
        if (this.analysisType === 'population') {
          this.$nextTick(() => {
            setTimeout(() => {
              this.createPopulationChart()
            }, 100)
          })
        }
      } catch (error) {
        console.error('Error loading population data:', error)
        this.error = 'Failed to load population data'
        this.populationData = this.getMockPopulationData()
        this.calculatePopulationStats()

        if (this.analysisType === 'population') {
          this.$nextTick(() => {
            setTimeout(() => {
              this.createPopulationChart()
            }, 100)
          })
        }
      } finally {
        this.isLoading = false
      }
    },

    async loadHistoricalData() {
      this.isLoading = true
      this.error = null

      try {
        const data = await analyticsService.getHistoricalData(this.selectedPeriod)
        this.historicalData = data
        this.calculateHistoricalStats()

        // 如果当前是历史分析模式，创建图表
        if (this.analysisType === 'historical') {
          this.createCurrentChart()
        }
      } catch (error) {
        console.error('Error loading historical data:', error)
        this.error = 'Failed to load historical data'
        this.historicalData = this.getMockHistoricalData()
        this.calculateHistoricalStats()

        if (this.analysisType === 'historical') {
          this.createCurrentChart()
        }
      } finally {
        this.isLoading = false
      }
    },

    createPopulationChart() {
      try {
        console.log('Creating population chart...')
        console.log('Population data:', this.populationData)

        // 确保销毁现有图表
        if (this.populationChart) {
          this.populationChart.destroy()
          this.populationChart = null
        }

        // 获取 canvas 元素
        const canvasId = 'population-chart-' + this.canvasKey
        const canvas = document.getElementById(canvasId)
        console.log('Canvas element found:', canvas)

        if (!canvas) {
          console.error(`Population chart canvas not found: ${canvasId}`)
          return
        }

        const ctx = canvas.getContext('2d')
        if (!ctx) {
          console.error('Could not get 2D context for population chart')
          return
        }

        // 检查数据
        if (!this.populationData || this.populationData.length === 0) {
          console.warn('No population data available for chart')
          return
        }

        const victoriaData = this.populationData.find(item => item.state === 'Vic.')
        console.log('Victoria data found:', victoriaData)

        if (!victoriaData) {
          console.warn('Victoria data not found in population dataset')
          return
        }

        console.log('Growth numbers:', victoriaData.growthNumbers)
        console.log('Growth rates:', victoriaData.growthRates)

        // 创建图表 - 使用最简化的配置避免clip错误
        this.populationChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: ['2016-17', '2017-18', '2018-19', '2019-20', '2020-21'],
            datasets: [{
              label: 'Population Growth',
              data: victoriaData.growthNumbers,
              borderColor: '#3498db',
              backgroundColor: '#3498db',
              borderWidth: 2,
              pointRadius: 4,
              pointHoverRadius: 6,
              fill: false,
              tension: 0
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false, // 禁用动画避免clip错误
            datasets: {
              line: {
                clip: false // 禁用clip功能
              }
            },
            elements: {
              point: {
                hoverRadius: 6
              },
              line: {
                tension: 0
              }
            },
            interaction: {
              intersect: false,
              mode: 'index'
            },
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                enabled: true,
                animation: false, // 禁用tooltip动画
                callbacks: {
                  label: function(context) {
                    const value = context.parsed.y
                    const percentage = victoriaData.growthRates[context.dataIndex]
                    return `Growth: ${value.toLocaleString()} people (${percentage}%)`
                  }
                }
              }
            },
            scales: {
              y: {
                beginAtZero: false,
                ticks: {
                  callback: function(value) {
                    return value >= 1000 ? (value / 1000).toFixed(0) + 'k' : value
                  }
                }
              },
              x: {
                ticks: {
                  maxRotation: 0
                }
              }
            }
          }
        })

        console.log('Population chart created successfully:', this.populationChart)
      } catch (error) {
        console.error('Error creating population chart:', error)
        this.error = 'Failed to create population chart: ' + error.message
      }
    },

    createHistoricalChart() {
      try {
        console.log('Creating historical chart...')
        console.log('Historical data:', this.historicalData)

        // 确保销毁现有图表
        if (this.historicalChart) {
          this.historicalChart.destroy()
          this.historicalChart = null
        }

        // 获取 canvas 元素
        const canvasId = 'historical-chart-' + this.canvasKey
        const canvas = document.getElementById(canvasId)
        console.log('Canvas element found:', canvas)

        if (!canvas) {
          console.error(`Historical chart canvas not found: ${canvasId}`)
          return
        }

        const ctx = canvas.getContext('2d')
        if (!ctx) {
          console.error('Could not get 2D context for historical chart')
          return
        }

        // 检查数据
        if (!this.historicalData || this.historicalData.length === 0) {
          console.warn('No historical data available for chart')
          return
        }

        const labels = this.historicalData.map(item => item.period)
        const occupancyData = this.historicalData.map(item => item.occupancyRate)

        console.log('Chart labels:', labels)
        console.log('Chart data:', occupancyData)

        // 创建图表 - 使用最简化的配置避免clip错误
        this.historicalChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: labels,
            datasets: [{
              label: 'Occupancy Rate',
              data: occupancyData,
              borderColor: '#e74c3c',
              backgroundColor: '#e74c3c',
              borderWidth: 2,
              pointRadius: 3,
              pointHoverRadius: 5,
              fill: false,
              tension: 0
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false, // 禁用动画避免clip错误
            datasets: {
              line: {
                clip: false // 禁用clip功能
              }
            },
            elements: {
              point: {
                hoverRadius: 5
              },
              line: {
                tension: 0
              }
            },
            interaction: {
              intersect: false,
              mode: 'index'
            },
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                enabled: true,
                animation: false, // 禁用tooltip动画
                callbacks: {
                  label: function(context) {
                    return `Occupancy: ${context.parsed.y.toFixed(1)}%`
                  }
                }
              }
            },
            scales: {
              y: {
                min: 0,
                max: 100,
                ticks: {
                  callback: function(value) {
                    return value + '%'
                  }
                }
              },
              x: {
                ticks: {
                  maxRotation: 0
                }
              }
            }
          }
        })

        console.log('Historical chart created successfully:', this.historicalChart)
      } catch (error) {
        console.error('Error creating historical chart:', error)
        this.error = 'Failed to create historical chart: ' + error.message
      }
    },

    calculatePopulationStats() {
      if (this.populationData.length === 0) return

      const victoriaData = this.populationData.find(item => item.state === 'Vic.')
      if (!victoriaData) return

      this.latestGrowthRate = victoriaData.growthRates[victoriaData.growthRates.length - 1]
      this.totalPopulationGrowth = victoriaData.growthNumbers.reduce((sum, num) => sum + num, 0)
    },

    calculateHistoricalStats() {
      if (this.historicalData.length === 0) return

      const peakData = this.historicalData.reduce((peak, current) =>
        current.occupancyRate > peak.occupancyRate ? current : peak
      )
      this.peakUsageTime = peakData.period

      const totalOccupancy = this.historicalData.reduce((sum, item) => sum + item.occupancyRate, 0)
      this.averageOccupancy = (totalOccupancy / this.historicalData.length).toFixed(1)
    },

    destroyAllCharts() {
      // Safely destroy chart instances
      try {
        if (this.populationChart) {
          this.populationChart.destroy()
          this.populationChart = null
          console.log('Population chart destroyed')
        }

        if (this.historicalChart) {
          this.historicalChart.destroy()
          this.historicalChart = null
          console.log('Historical chart destroyed')
        }
      } catch (error) {
        console.error('Error destroying charts:', error)
      }
    },

    retryAnalysis() {
      if (this.analysisType === 'population') {
        this.loadPopulationData()
      } else {
        this.loadHistoricalData()
      }
    },

    getMockPopulationData() {
      return [{
        state: 'Vic.',
        growthNumbers: [209495, 214408, 236429, 215728, 188855],
        growthRates: ['4.2', '4.2', '4.5', '4.0', '3.5']
      }]
    },

    getMockHistoricalData() {
      const mockData = []
      const days = this.selectedPeriod === '7d' ? 7 : this.selectedPeriod === '1m' ? 30 : 90

      for (let i = 0; i < Math.min(days, 20); i++) {
        const date = new Date()
        date.setDate(date.getDate() - i)

        mockData.unshift({
          period: date.toLocaleDateString('en-AU', {day: 'numeric', month: 'short'}),
          occupancyRate: 60 + Math.sin(i * 0.2) * 20 + Math.random() * 10,
          availableSpots: 1200 + Math.cos(i * 0.3) * 400
        })
      }

      return mockData
    }
  }
}
</script>

<style scoped>
.analytics-panel {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

/* Analysis Type Selection */
.analysis-type-selection {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.analysis-btn {
  background-color: #ecf0f1;
  color: #2c3e50;
  border: none;
  padding: 0.4rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  flex: 1;
  transition: all 0.2s;
}

.analysis-btn:hover {
  background-color: #d5dbdb;
}

.analysis-btn.active {
  background-color: #3498db;
  color: white;
}

/* Analysis Content */
.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.chart-container {
  height: 180px;
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 0.5rem;
  border: 1px solid #e1e8ed;
  position: relative;
}

/* Time Period Selector */
.time-period-selector {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.time-period-selector select {
  padding: 0.3rem 0.5rem;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #2c3e50;
  background-color: white;
}

/* Analysis Summary */
.analysis-summary {
  display: flex;
  justify-content: space-around;
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 0.5rem;
  border-left: 3px solid #3498db;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  color: #7f8c8d;
  font-size: 0.7rem;
  font-weight: 500;
}

.stat-value {
  display: block;
  color: #2c3e50;
  font-size: 0.9rem;
  font-weight: 600;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
  gap: 0.5rem;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #ecf0f1;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-state p {
  font-size: 0.8rem;
  color: #7f8c8d;
  margin: 0;
}

/* Error State */
.error-state {
  text-align: center;
  padding: 1rem 0;
}

.error-state p {
  color: #e74c3c;
  font-size: 0.8rem;
  margin-bottom: 0.5rem;
}

.retry-btn {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
}

/* Animations */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive Adjustments */
@media (max-width: 480px) {
  .analysis-type-selection {
    flex-direction: column;
  }

  .analysis-summary {
    flex-direction: column;
    gap: 0.5rem;
  }

  .stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-label, .stat-value {
    display: inline;
  }
}
</style>
