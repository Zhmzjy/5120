// Dashboard related routes
import Dashboard from '../views/Dashboard.vue'

export const dashboardRoutes = [
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: 'Parking Dashboard'
    }
  },
  {
    path: '/map',
    name: 'ParkingMap',
    component: Dashboard, // You can create a separate MapView component later
    meta: {
      title: 'Parking Map'
    }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: Dashboard, // You can create a separate AnalyticsView component later
    meta: {
      title: 'Parking Analytics'
    }
  },
  {
    path: '/predictions',
    name: 'Predictions',
    component: Dashboard, // You can create a separate PredictionsView component later
    meta: {
      title: 'Parking Predictions'
    }
  }
]
