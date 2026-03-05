import "./Footer.css";
import logo from "../assets/ktulogo.png";

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-body">

        {/* ── BRAND ── */}
        <div className="footer-brand">
          <div className="footer-logo">
            <div className="footer-logo-img-wrap">
              <img src={logo} alt="AISAT" className="footer-logo-img" />
            </div>
            <div className="footer-logo-text">
              <span className="footer-logo-name">KTU Result Parser</span>
              <span className="footer-logo-tag">AISAT  Result Intelligence</span>
            </div>
          </div>
          <p className="footer-brand-desc">
            Automated KTU result PDF processing — parse, structure, and export
            student grade data to clean Excel reports in seconds.
            Built at AISAT College of Engineering, Kerala.
          </p>
        </div>

        {/* ── LINKS ── */}
        <div className="footer-links-group">

          <div className="footer-col">
            <div className="footer-col-title">Project</div>
            <a
              className="footer-link"
              href="https://github.com/AlexJoBobby770/ktu-result-parser"
              target="_blank"
              rel="noopener noreferrer"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
              </svg>
              GitHub Repository
            </a>
            <a
              className="footer-link"
              href="https://github.com/AlexJoBobby770/ktu-result-parser"
              target="_blank"
              rel="noopener noreferrer"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              Documentation
            </a>
          </div>

          <div className="footer-col">
            <div className="footer-col-title">College</div>
            <a
              className="footer-link"
              href="https://aisat.ac.in"
              target="_blank"
              rel="noopener noreferrer"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="2" y1="12" x2="22" y2="12"/>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
              </svg>
              AISAT Website
            </a>
            <a
              className="footer-link"
              href="https://ktu.edu.in"
              target="_blank"
              rel="noopener noreferrer"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="2" y1="12" x2="22" y2="12"/>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
              </svg>
              KTU Portal
            </a>
          </div>

          <div className="footer-col">
            <div className="footer-col-title">Built With</div>
            <a className="footer-link" href="https://fastapi.tiangolo.com" target="_blank" rel="noopener noreferrer">FastAPI</a>
            <a className="footer-link" href="https://react.dev" target="_blank" rel="noopener noreferrer">React</a>
            <a className="footer-link" href="https://firebase.google.com" target="_blank" rel="noopener noreferrer">Firebase Auth</a>
            <a className="footer-link" href="https://openpyxl.readthedocs.io" target="_blank" rel="noopener noreferrer">OpenPyXl</a>
          </div>

        </div>
      </div>

      <div className="footer-divider" />

      <div className="footer-bottom">
        <span className="footer-copyright">
          © 2026 KTU Processor. All Rights Reserved.
        </span>
      </div>
    </footer>
  );
}

export default Footer;