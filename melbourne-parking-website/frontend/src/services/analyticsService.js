/**
 * Analytics Service for Advanced Analysis Features
 * Handles population data and historical trends analysis
 */

import axios from 'axios'
import config from '../config/api.js'

// Use unified API configuration
const API_BASE_URL = `${config.API_BASE_URL}/api`

class AnalyticsService {

  /**
   * Get population growth data for Victoria
   * @returns {Promise<Array>} Population data with growth numbers and rates
   */
  async getPopulationData() {
    try {
      const response = await axios.get(`${API_BASE_URL}/analytics/population`)
      return response.data
    } catch (error) {
      console.error('Error fetching population data:', error)
      throw error
    }
  }

  /**
   * Get historical parking usage trends
   * @param {string} period - Time period ('7d', '1m', '3m')
   * @returns {Promise<Array>} Historical data with occupancy rates and available spots
   */
  async getHistoricalData(period = '1m') {
    try {
      const response = await axios.get(`${API_BASE_URL}/analytics/historical`, {
        params: { period }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching historical data:', error)
      throw error
    }
  }

  /**
   * Get correlation analysis between population and parking
   * @returns {Promise<Object>} Correlation analysis results
   */
  async getPopulationParkingCorrelation() {
    try {
      const response = await axios.get(`${API_BASE_URL}/analytics/correlation`)
      return response.data
    } catch (error) {
      console.error('Error fetching correlation data:', error)
      throw error
    }
  }

  /**
   * Process CSV population data (client-side processing as fallback)
   * @param {string} csvData - Raw CSV data
   * @returns {Array} Processed population data
   */
  processPopulationCSV(csvData) {
    const lines = csvData.split('\n')
    const data = []

    // Skip header rows and process data
    for (let i = 2; i < lines.length; i++) {
      const line = lines[i].trim()
      if (!line) continue

      const columns = this.parseCSVLine(line)
      if (columns.length >= 10) {
        const state = columns[0].replace(/"/g, '')

        // Extract growth numbers (columns 1, 3, 5, 7, 9)
        const growthNumbers = [
          this.parseNumber(columns[1]),
          this.parseNumber(columns[3]),
          this.parseNumber(columns[5]),
          this.parseNumber(columns[7]),
          this.parseNumber(columns[9])
        ].filter(num => !isNaN(num))

        // Extract growth rates (columns 2, 4, 6, 8, 10)
        const growthRates = [
          columns[2].replace(/"/g, ''),
          columns[4].replace(/"/g, ''),
          columns[6].replace(/"/g, ''),
          columns[8].replace(/"/g, ''),
          columns[10].replace(/"/g, '')
        ].filter(rate => rate && rate !== '')

        if (growthNumbers.length > 0 && growthRates.length > 0) {
          data.push({
            state,
            growthNumbers,
            growthRates
          })
        }
      }
    }

    return data
  }

  /**
   * Parse CSV line handling quoted values
   * @param {string} line - CSV line
   * @returns {Array} Parsed columns
   */
  parseCSVLine(line) {
    const columns = []
    let current = ''
    let inQuotes = false

    for (let i = 0; i < line.length; i++) {
      const char = line[i]

      if (char === '"') {
        inQuotes = !inQuotes
      } else if (char === ',' && !inQuotes) {
        columns.push(current.trim())
        current = ''
      } else {
        current += char
      }
    }

    // Add the last column
    columns.push(current.trim())
    return columns
  }

  /**
   * Parse number from string, handling commas
   * @param {string} str - String to parse
   * @returns {number} Parsed number
   */
  parseNumber(str) {
    if (!str) return NaN
    const cleaned = str.replace(/[",]/g, '')
    return parseFloat(cleaned)
  }

  /**
   * Generate mock historical data for development/fallback
   * @param {string} period - Time period
   * @returns {Array} Mock historical data
   */
  generateMockHistoricalData(period) {
    const data = []
    const days = period === '7d' ? 7 : period === '1m' ? 30 : 90

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)

      // Generate realistic parking patterns
      const hour = date.getHours()
      let baseOccupancy = 30 // Base occupancy rate

      // Peak hours pattern
      if (hour >= 8 && hour <= 10) baseOccupancy = 75 // Morning peak
      else if (hour >= 12 && hour <= 14) baseOccupancy = 65 // Lunch peak
      else if (hour >= 17 && hour <= 19) baseOccupancy = 80 // Evening peak
      else if (hour >= 20 || hour <= 6) baseOccupancy = 20 // Night/early morning

      // Weekend adjustment
      if (date.getDay() === 0 || date.getDay() === 6) {
        baseOccupancy *= 0.7 // Lower weekend usage
      }

      // Add some randomness
      const occupancyRate = Math.max(10, Math.min(95, baseOccupancy + (Math.random() - 0.5) * 20))
      const totalSpots = 3200
      const occupiedSpots = Math.round(totalSpots * occupancyRate / 100)
      const availableSpots = totalSpots - occupiedSpots

      data.push({
        period: period === '7d'
          ? date.toLocaleDateString('en-AU', { weekday: 'short', month: 'short', day: 'numeric' })
          : date.toLocaleDateString('en-AU', { month: 'short', day: 'numeric' }),
        occupancyRate: Math.round(occupancyRate * 10) / 10,
        availableSpots,
        occupiedSpots,
        totalSpots,
        timestamp: date.toISOString()
      })
    }

    return data
  }

  /**
   * Calculate trend statistics from historical data
   * @param {Array} data - Historical data array
   * @returns {Object} Trend statistics
   */
  calculateTrendStats(data) {
    if (!data || data.length === 0) {
      return {
        averageOccupancy: 0,
        peakOccupancy: 0,
        peakTime: 'N/A',
        trendDirection: 'stable',
        changeRate: 0
      }
    }

    const occupancyRates = data.map(d => d.occupancyRate)
    const averageOccupancy = occupancyRates.reduce((sum, rate) => sum + rate, 0) / occupancyRates.length

    const peakData = data.reduce((max, current) =>
      current.occupancyRate > max.occupancyRate ? current : max
    )

    // Calculate trend
    const firstRate = occupancyRates[0]
    const lastRate = occupancyRates[occupancyRates.length - 1]
    const changeRate = ((lastRate - firstRate) / firstRate) * 100

    let trendDirection = 'stable'
    if (changeRate > 5) trendDirection = 'increasing'
    else if (changeRate < -5) trendDirection = 'decreasing'

    return {
      averageOccupancy: Math.round(averageOccupancy * 10) / 10,
      peakOccupancy: peakData.occupancyRate,
      peakTime: peakData.period,
      trendDirection,
      changeRate: Math.round(changeRate * 10) / 10
    }
  }
}

const analyticsService = new AnalyticsService()
export default analyticsService
