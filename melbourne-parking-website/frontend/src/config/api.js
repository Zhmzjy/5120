// Environment configuration for different deployment stages
const config = {
  development: {
    API_BASE_URL: 'http://localhost:5002'
  },
  production: {
    API_BASE_URL: import.meta.env.VITE_API_URL || 'https://te21-fit5120-production.up.railway.app'
  }
}

const currentConfig = config[import.meta.env.MODE] || config.development

export default currentConfig
