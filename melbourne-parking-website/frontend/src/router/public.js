// Landing page and public routes
import LandingPage from '../views/LandingPage.vue'

export const publicRoutes = [
  {
    path: '/',
    name: 'Landing',
    component: LandingPage,
    meta: {
      title: 'Melbourne Parking Solutions',
      public: true
    }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue'), // Lazy loading
    meta: {
      title: 'About Us',
      public: true
    }
  },
  {
    path: '/contact',
    name: 'Contact',
    component: () => import('../views/Contact.vue'), // Lazy loading
    meta: {
      title: 'Contact Us',
      public: true
    }
  }
]
