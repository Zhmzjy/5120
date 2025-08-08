import axios from 'axios'

// Use relative path for production deployment, fallback to localhost for development
const API_BASE_URL = process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:5002/api'

class ParkingService {
  async getCurrentParkingStatus() {
    const response = await axios.get(`${API_BASE_URL}/parking/current`)
    return response.data
  }

  async findNearbyParking(lat, lng, radius = 500) {
    const response = await axios.get(`${API_BASE_URL}/parking/nearby`, {
      params: { lat, lng, radius }
    })
    return response.data
  }

  async getStreetsList() {
    const response = await axios.get(`${API_BASE_URL}/parking/streets`)
    return response.data
  }

  async getOverviewStats() {
    const response = await axios.get(`${API_BASE_URL}/statistics/overview`)
    return response.data
  }

  async getZoneStats() {
    const response = await axios.get(`${API_BASE_URL}/statistics/zones`)
    return response.data
  }
}

export default new ParkingService()
