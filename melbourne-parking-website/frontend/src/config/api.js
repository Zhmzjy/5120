// Environment configuration for different deployment stages
const config = {
  development: {
    API_BASE_URL: 'http://localhost:5002'
  },
  production: {
    // Replace with your actual Render backend URL
    API_BASE_URL: import.meta.env.VITE_API_URL || 'https://melbourne-parking-backend.onrender.com'
  }
}

const currentConfig = config[import.meta.env.MODE] || config.development

export default currentConfig
