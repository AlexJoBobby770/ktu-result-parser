import { useRef, useEffect } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import "./Features.css";

gsap.registerPlugin(ScrollTrigger);

const features = [
  {
    title: "Lightning Fast",
    description:
      "Process hundreds of records in seconds with our optimized parsing engine",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
        <polygon
          points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  {
    title: "100% Accurate",
    description:
      "Advanced algorithms ensure zero data loss and perfect format conversion",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
        <line x1="12" y1="1" x2="12" y2="23" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <path
          d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  {
    title: "Secure",
    description:
      "Your data is encrypted and protected with JWT authentication",
    icon: (
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
        <rect
          x="3"
          y="11"
          width="18"
          height="11"
          rx="2"
          ry="2"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M7 11V7a5 5 0 0 1 10 0v4"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
];

function Features() {
  const cardsRef = useRef([]);

  useEffect(() => {
    cardsRef.current.forEach((card, index) => {
      if (card) {
        gsap.fromTo(
          card,
          { opacity: 0, y: 30 },
          {
            opacity: 1,
            y: 0,
            duration: 0.8,
            delay: index * 0.15,
            ease: "power3.out",
            scrollTrigger: {
              trigger: card,
              start: "top 85%",
            },
          }
        );
      }
    });
  }, []);

  return (
    <section className="features-section">
      <div className="section-header">
        <h2 className="section-title">Why Choose Us</h2>
        <p className="section-description">
          Built for speed, accuracy, and simplicity
        </p>
      </div>

      <div className="features-grid">
        {features.map((feature, index) => (
          <div
            key={feature.title}
            className="feature-card"
            ref={(el) => (cardsRef.current[index] = el)}
          >
            <div className="feature-icon">{feature.icon}</div>
            <h3 className="feature-title">{feature.title}</h3>
            <p className="feature-description">{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Features;