import "./Footer.css";
import logo from "../assets/ktulogo.png";

const LINKS = {
  project: [
    {
      label: "GitHub Repository",
      href: "https://github.com/AlexJoBobby770/ktu-result-parser",
      icon: (
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
        </svg>
      ),
    },
    {
      label: "Documentation",
      href: "https://github.com/AlexJoBobby770/ktu-result-parser",
      icon: (
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>
      ),
    },
  ],
  college: [
    {
      label: "AISAT Website",
      href: "https://aisat.ac.in",
      icon: (
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="2" y1="12" x2="22" y2="12"/>
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
        </svg>
      ),
    },
    {
      label: "KTU Portal",
      href: "https://ktu.edu.in",
      icon: (
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="2" y1="12" x2="22" y2="12"/>
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
        </svg>
      ),
    },
  ],
  stack: [
    { label: "FastAPI",      href: "https://fastapi.tiangolo.com" },
    { label: "React",        href: "https://react.dev" },
    { label: "Firebase Auth",href: "https://firebase.google.com" },
    { label: "OpenPyXL",     href: "https://openpyxl.readthedocs.io" },
  ],
};

function Footer() {
  return (
    <footer className="fo">

      {/* ── Top band ── */}
      <div className="fo__top">
        <div className="fo__inner">

          {/* Brand column */}
          <div className="fo__brand">
            <div className="fo__logo">
              <div className="fo__logo-img-box">
                <img src={logo} alt="AISAT" className="fo__logo-img" />
              </div>
              <div className="fo__logo-copy">
                <span className="fo__logo-product">KTU Result Parser</span>
                <span className="fo__logo-org">AISAT College of Engineering</span>
              </div>
            </div>
            <p className="fo__brand-desc">
              Automated KTU result PDF processing — parse, structure, and export
              student grade data to clean Excel reports in seconds.
              Built for faculty at AISAT, Ernakulam, Kerala.
            </p>

            {/* Trust pills */}
            <div className="fo__trust">
              <span className="fo__trust-pill">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
                Firebase secured
              </span>
              <span className="fo__trust-pill">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  <rect x="3" y="11" width="18" height="11" rx="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                Zero data retention
              </span>
            </div>
          </div>

          {/* Link columns */}
          <div className="fo__cols">

            <div className="fo__col">
              <p className="fo__col-head">Project</p>
              {LINKS.project.map(l => (
                <a key={l.label} href={l.href} className="fo__link" target="_blank" rel="noopener noreferrer">
                  {l.icon}
                  {l.label}
                </a>
              ))}
            </div>

            <div className="fo__col">
              <p className="fo__col-head">College</p>
              {LINKS.college.map(l => (
                <a key={l.label} href={l.href} className="fo__link" target="_blank" rel="noopener noreferrer">
                  {l.icon}
                  {l.label}
                </a>
              ))}
            </div>

            <div className="fo__col">
              <p className="fo__col-head">Built with</p>
              {LINKS.stack.map(l => (
                <a key={l.label} href={l.href} className="fo__link" target="_blank" rel="noopener noreferrer">
                  {l.label}
                </a>
              ))}
            </div>

          </div>
        </div>
      </div>

      {/* ── Bottom bar ── */}
      <div className="fo__bottom">
        <div className="fo__bottom-inner">
          <span className="fo__copy">
            © {new Date().getFullYear()} KTU Result Parser · AISAT College of Engineering. All rights reserved.
          </span>
          <div className="fo__bottom-links">
            <a href="#" className="fo__bottom-link">Privacy</a>
            <span className="fo__bottom-sep" />
            <a href="#" className="fo__bottom-link">Terms</a>
          </div>
        </div>
      </div>

    </footer>
  );
}

export default Footer;