import { useRef, useEffect } from "react";
import { gsap } from "gsap";
import "./Hero.css";

function Hero({ uploadSectionRef }) {
  const heroRef = useRef(null);

  useEffect(() => {
    if (heroRef.current) {
      gsap.fromTo(
        heroRef.current.children,
        { opacity: 0, y: 30 },
        {
          opacity: 1,
          y: 0,
          duration: 1,
          stagger: 0.2,
          ease: "power3.out",
        }
      );
    }
  }, []);

  const scrollToUpload = () => {
    uploadSectionRef?.current?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="hero">
      <div className="hero-content" ref={heroRef}>
        <h1 className="hero-title">
          Transform KTU Results
          <br />
          Into Structured Data
        </h1>
        <p className="hero-subtitle">
          Automated processing for KTU result PDFs. Upload, process, and
          download structured Excel reports in seconds.
        </p>
        <div className="hero-cta">
          <button className="btn-primary" onClick={scrollToUpload}>
            Get Started
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path
                d="M7 13L13 7M13 7H7M13 7V13"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>
      </div>
    </section>
  );
}

export default Hero;