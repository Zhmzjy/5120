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
          <a href="#about" class="nav-link">About</a>
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
        </div>
      </div>
      <div class="scroll-indicator" @click="scrollToFeatures">
        <div class="scroll-arrow"></div>
      </div>
    </section>

    <!-- Features Preview -->
    <section class="features-section" id="features">
      <div class="container">
        <h2 class="section-title">Smart Parking Solutions</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">📍</div>
            <h3>Real-time Status</h3>
            <p>Live updates on parking availability across Melbourne CBD</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔥</div>
            <h3>Heat Map View</h3>
            <p>Visualize parking density and find the best areas to park</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3>Smart Search</h3>
            <p>Find nearby available parking spaces with distance calculation</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Analytics</h3>
            <p>Detailed statistics and insights about parking patterns</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="how-it-works-section">
      <div class="container">
        <h2 class="section-title">How It Works</h2>
        <div class="steps-grid">
          <div class="step-card">
            <div class="step-number">1</div>
            <h3>Search Location</h3>
            <p>Enter your destination or browse the interactive map</p>
          </div>
          <div class="step-card">
            <div class="step-number">2</div>
            <h3>View Availability</h3>
            <p>See real-time parking status and available spaces</p>
          </div>
          <div class="step-card">
            <div class="step-number">3</div>
            <h3>Park Smart</h3>
            <p>Navigate to your chosen parking spot and save time</p>
          </div>
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
            <div class="stat-number">24/7</div>
            <div class="stat-label">Live Updates</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">Free</div>
            <div class="stat-label">Service</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Final CTA -->
    <section class="cta-section" id="about">
      <div class="container">
        <h2>Ready to Stop Circling?</h2>
        <p>Join thousands of Melbourne drivers who've already discovered smarter parking.</p>
        <button @click="goToDashboard" class="btn btn-explore">Explore</button>
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
    scrollToFeatures() {
      document.getElementById('features').scrollIntoView({
        behavior: 'smooth'
      })
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
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 3rem;
  color: #2c3e50;
}

.stats-section .section-title {
  color: white;
}

/* Feature Cards */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #2c3e50;
}

/* Steps */
.steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 3rem;
}

.step-card {
  text-align: center;
}

.step-number {
  width: 60px;
  height: 60px;
  background-color: #3498db;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0 auto 1.5rem;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  text-align: center;
}

.stat-number {
  font-size: 3rem;
  font-weight: bold;
  color: #3498db;
}

.stat-label {
  font-size: 1.2rem;
  margin-top: 0.5rem;
}

/* CTA Section */
.cta-section h2 {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.cta-section p {
  font-size: 1.3rem;
  margin-bottom: 2rem;
  color: #666;
}

.btn-explore {
  background-color: #27ae60;
  color: white;
  font-size: 1.3rem;
  padding: 1.2rem 3rem;
}

.btn-explore:hover {
  background-color: #229954;
  transform: translateY(-2px);
}

/* Footer */
.footer {
  background-color: #2c3e50;
  color: white;
  text-align: center;
  padding: 2rem 0;
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateX(-50%) translateY(0);
  }
  40% {
    transform: translateX(-50%) translateY(-10px);
  }
  60% {
    transform: translateX(-50%) translateY(-5px);
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }

  .hero-buttons {
    flex-direction: column;
    align-items: center;
  }

  .btn {
    width: 100%;
    max-width: 300px;
  }

  .features-grid,
  .steps-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
