<template>
  <div class="landing-page">
    <!-- Navigation Bar -->
    <nav class="navbar" :class="{ 'navbar-scrolled': isScrolled }">
      <div class="nav-container">
        <div class="nav-logo">
          <h3>Melbourne Parking</h3>
        </div>
        <div class="nav-menu">
          <a href="#features" class="nav-link">Find Parking</a>
          <a href="#contact" class="nav-link">Contact</a>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <h1 class="hero-title">No More Circling the Block.</h1>
        <h4 class="hero-subtitle">Get real-time parking data for Melbourne's CBD—less time driving, more time living.</h4>
        <div class="hero-buttons">
          <button @click="goToDashboard" class="btn btn-primary">Find Parking Now</button>
          <button @click="scrollToFeatures" class="btn btn-secondary">Learn More</button>
          <button @click="$router.push('/analytics')" class="btn btn-secondary">View Analytics</button>
        </div>
      </div>
      <div class="scroll-indicator" @click="scrollToFeatures">
        <div class="scroll-arrow"></div>
      </div>
    </section>

    <!-- Features Preview -->
    <section class="features-section" id="features">
      <div class="container">
        <h2 class="section-title">
          Smart Parking Solutions
          <div class="title-underline"></div>
        </h2>
        <div class="features-grid">
          <div class="feature-card" @mouseenter="animateFeature" @mouseleave="resetFeature">
            <div class="feature-icon-wrapper">
              <div class="feature-icon-bg"></div>
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                </svg>
              </div>
            </div>
            <h3>Real-time Status</h3>
            <p>Live updates on parking availability across Melbourne CBD with instant notifications</p>
          </div>
          <div class="feature-card" @mouseenter="animateFeature" @mouseleave="resetFeature">
            <div class="feature-icon-wrapper">
              <div class="feature-icon-bg"></div>
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              </div>
            </div>
            <h3>Heat Map View</h3>
            <p>Visualize parking density and discover optimal areas to park with color-coded insights</p>
          </div>
          <div class="feature-card" @mouseenter="animateFeature" @mouseleave="resetFeature">
            <div class="feature-icon-wrapper">
              <div class="feature-icon-bg"></div>
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                </svg>
              </div>
            </div>
            <h3>Smart Search</h3>
            <p>Find nearby available parking spaces with precise distance calculation and route guidance</p>
          </div>
          <div class="feature-card" @mouseenter="animateFeature" @mouseleave="resetFeature">
            <div class="feature-icon-wrapper">
              <div class="feature-icon-bg"></div>
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
                </svg>
              </div>
            </div>
            <h3>Analytics</h3>
            <p>Detailed statistics and insights about parking patterns to help you make informed decisions</p>
          </div>
        </div>

        <!-- CTA Section integrated -->
        <div class="integrated-cta">
          <h2>Ready to Stop Circling?</h2>
          <p>Join thousands of Melbourne drivers who've already discovered smarter parking.</p>
          <button @click="goToDashboard" class="btn btn-explore">Explore</button>
        </div>
      </div>
    </section>

    <!-- Statistics Highlight -->
    <section class="stats-section">
      <div class="container">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">5000+</div>
            <div class="stat-label">Parking Bays</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">CBD</div>
            <div class="stat-label">Coverage Area</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">10/8</div>
            <div class="stat-label">Live Updates</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">Free</div>
            <div class="stat-label">Service</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer" id="contact">
      <div class="container">
        <p>&copy; 2025 Melbourne Parking System. Making parking easier, one spot at a time.</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'LandingPage',
  data() {
    return {
      isScrolled: false
    }
  },
  mounted() {
    window.addEventListener('scroll', this.handleScroll)
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.handleScroll)
  },
  methods: {
    handleScroll() {
      this.isScrolled = window.scrollY > 50
    },
    goToDashboard() {
      this.$router.push('/dashboard')
    },
    goToAnalytics() {
    this.$router.push('/analytics')
    },
    scrollToFeatures() {
      document.getElementById('features').scrollIntoView({
        behavior: 'smooth'
      })
    },
    animateFeature(event) {
      const card = event.currentTarget;
      card.querySelector('.feature-icon').classList.add('animate');
    },
    resetFeature(event) {
      const card = event.currentTarget;
      card.querySelector('.feature-icon').classList.remove('animate');
    }
  }
}
</script>

<style scoped>
/* Navigation */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: transparent;
  transition: all 0.3s ease;
  z-index: 1000;
  padding: 1rem 0;
}

.navbar-scrolled {
  background-color: rgba(44, 62, 80, 0.95);
  backdrop-filter: blur(10px);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo h3 {
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-menu {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: #3498db;
}

/* Hero Section */
.hero-section {
  height: 100vh;
  background-image: url('/pexels-paul-macallan-5033748.jpg');
  background-size: cover;
  background-position: center;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0,0,0,0.6), rgba(0,0,0,0.4));
}

.hero-content {
  position: relative;
  z-index: 2;
  text-align: center;
  color: white;
  max-width: 800px;
  padding: 0 2rem;
  animation: fadeInUp 1s ease-out;
}

.hero-title {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: bold;
  margin-bottom: 1.5rem;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: clamp(1.1rem, 2.5vw, 1.5rem);
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 3rem;
  line-height: 1.4;
}

.hero-buttons {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: transparent;
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background-color: white;
  color: #2c3e50;
  transform: translateY(-2px);
}

.scroll-indicator {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  cursor: pointer;
  animation: bounce 2s infinite;
}

.scroll-arrow {
  width: 24px;
  height: 24px;
  border-right: 2px solid white;
  border-bottom: 2px solid white;
  transform: rotate(45deg);
}

/* Sections */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.features-section,
.how-it-works-section,
.stats-section,
.cta-section {
  padding: 5rem 0;
}

.features-section {
  background-color: #f8f9fa;
}

.how-it-works-section {
  background-color: white;
}

.stats-section {
  background-color: #2c3e50;
  color: white;
}

.cta-section {
  background-color: #f8f9fa;
  text-align: center;
}

.section-title {
  position: relative;
  font-size: 2.8rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 4rem;
  color: #2c3e50;
}

.title-underline {
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #3498db, #2980b9);
  margin: 1rem auto 0;
  border-radius: 2px;
  position: relative;
  overflow: hidden;
}

.title-underline::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
  animation: shimmer 2s ease-in-out infinite;
}

.stats-section .section-title {
  color: white;
}

/* Feature Cards Enhanced */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2.5rem;
  margin-top: 4rem;
}

.feature-card {
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
  padding: 2.5rem 2rem;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 8px 25px rgba(0,0,0,0.08);
  border: 1px solid rgba(255,255,255,0.2);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #3498db, #2980b9);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(52, 152, 219, 0.15);
}

.feature-card:hover::before {
  opacity: 1;
}

.feature-icon-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 2rem;
}

.feature-icon-bg {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(41, 128, 185, 0.2));
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: all 0.3s ease;
}

.feature-icon {
  position: relative;
  width: 48px;
  height: 48px;
  color: #3498db;
  z-index: 2;
  transition: all 0.3s ease;
}

.feature-icon.animate {
  transform: rotate(360deg) scale(1.1);
  color: #2980b9;
}

.feature-card:hover .feature-icon-bg {
  transform: translate(-50%, -50%) scale(1.2);
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.2), rgba(41, 128, 185, 0.3));
}

.feature-card h3 {
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #2c3e50;
  transition: color 0.3s ease;
}

.feature-card:hover h3 {
  color: #3498db;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
  font-size: 1rem;
}

/* Integrated CTA within Features Section */
.integrated-cta {
  text-align: center;
  margin-top: 4rem;
  padding: 3rem 2rem;
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.05), rgba(41, 128, 185, 0.08));
  border-radius: 20px;
  border: 1px solid rgba(52, 152, 219, 0.1);
}

.integrated-cta h2 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.integrated-cta p {
  font-size: 1.3rem;
  margin-bottom: 2rem;
  color: #666;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.btn-explore {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  font-size: 1.3rem;
  font-weight: 600;
  padding: 1.2rem 3rem;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(52, 152, 219, 0.3);
  transition: all 0.3s ease;
}

.btn-explore:hover {
  background: linear-gradient(135deg, #2980b9, #1f5f8b);
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(52, 152, 219, 0.4);
}

/* Enhanced Stats Section */
.stats-section {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  color: white;
  padding: 4rem 0;
  position: relative;
  overflow: hidden;
}

.stats-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    radial-gradient(circle at 25% 25%, rgba(52, 152, 219, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 75% 75%, rgba(52, 152, 219, 0.08) 0%, transparent 50%);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 3rem;
  text-align: center;
  position: relative;
  z-index: 2;
  max-width: 1000px;
  margin: 0 auto;
}

.stat-item {
  padding: 2rem 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.stat-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 800;
  color: #3498db;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  line-height: 1;
}

.stat-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  line-height: 1.3;
}

/* Remove old CTA section styles since it's now integrated */
.cta-section {
  display: none;
}

/* Responsive Design for Stats */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem;
  }

  .stat-number {
    font-size: 2.2rem;
  }

  .stat-label {
    font-size: 0.85rem;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    max-width: 400px;
  }

  .stat-item {
    padding: 1.5rem 1rem;
  }

  .stat-number {
    font-size: 2rem;
  }

  .stat-label {
    font-size: 0.8rem;
  }

  .integrated-cta {
    margin-top: 3rem;
    padding: 2rem 1.5rem;
  }

  .integrated-cta h2 {
    font-size: 2rem;
  }

  .integrated-cta p {
    font-size: 1.1rem;
  }
}

/* Animation for stats when in view */
.stat-item {
  animation: fadeInUp 0.6s ease-out;
}

.stat-item:nth-child(1) { animation-delay: 0.1s; }
.stat-item:nth-child(2) { animation-delay: 0.2s; }
.stat-item:nth-child(3) { animation-delay: 0.3s; }
.stat-item:nth-child(4) { animation-delay: 0.4s; }

/* Enhanced Animations */
@keyframes pulse {
  0%, 100% {
    opacity: 0.6;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 0.8;
    transform: translate(-50%, -50%) scale(1.1);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes progressFill {
  0% {
    width: 0%;
  }
  33% {
    width: 33.33%;
  }
  66% {
    width: 66.66%;
  }
  100% {
    width: 100%;
  }
}

@keyframes dotPulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
}

/* Responsive Design Enhanced */
@media (max-width: 1024px) {
  .steps-container {
    flex-direction: column;
    align-items: center;
  }

  .step-arrow {
    transform: rotate(90deg);
    margin: 1rem 0;
  }
}

@media (max-width: 768px) {
  .features-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .feature-card {
    padding: 2rem 1.5rem;
  }

  .step-card {
    min-width: auto;
    padding: 1.5rem;
  }

  .step-arrow {
    display: none;
  }

  .progress-indicator {
    margin-top: 2rem;
  }
}

/* Additional improvements for section titles */
.section-title {
  position: relative;
  font-size: 2.8rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 4rem;
  color: #2c3e50;
}

.title-underline {
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #3498db, #2980b9);
  margin: 1rem auto 0;
  border-radius: 2px;
  position: relative;
  overflow: hidden;
}

.title-underline::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
  animation: shimmer 2s ease-in-out infinite;
}

@keyframes shimmer {
  0% {
    left: -100%;
  }
  50%, 100% {
    left: 100%;
  }
}
</style>
