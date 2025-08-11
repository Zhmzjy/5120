// Environment configuration for different deployment stages
const config = {
  development: {
    API_BASE_URL: 'http://localhost:5002'
  },
  production: {
    // Render backend URL - will be updated after backend deployment
    API_BASE_URL: import.meta.env.VITE_API_URL || 'https://your-render-backend.onrender.com'
  }
}

const currentConfig = config[import.meta.env.MODE] || config.development

export default currentConfig
