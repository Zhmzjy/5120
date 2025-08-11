// Environment configuration for different deployment stages
const config = {
  development: {
    API_BASE_URL: 'http://localhost:5002'
  },
  production: {
    API_BASE_URL: process.env.VUE_APP_API_URL || 'https://your-railway-app.railway.app'
  }
}

const currentConfig = config[process.env.NODE_ENV] || config.development

export default currentConfig
