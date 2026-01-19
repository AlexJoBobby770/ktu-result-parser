import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import DotGrid from './DotGrid';
import MagicBento from './MagicBento'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <div style={{ width: '100%', height: '100vh', position: 'fixed', top: 0, left: 0, zIndex: -1 }}>
      <DotGrid
        dotSize={4}
        gap={16}
        baseColor="#271e37"
        activeColor="#407a2c"
        proximity={100}
        speedTrigger={60}
        shockRadius={230}
        shockStrength={5}
        maxSpeed={5000}
        resistance={450}
        returnDuration={1.2}
      />
    </div>

<MagicBento 
  textAutoHide={true}
  enableStars={true}
  enableSpotlight={true}
  enableBorderGlow={true}
  enableTilt={true}
  enableMagnetism={true}
  clickEffect={true}
  spotlightRadius={300}
  particleCount={12}
  glowColor="132, 0, 255"
/>
    <App />
  </StrictMode>,
)
