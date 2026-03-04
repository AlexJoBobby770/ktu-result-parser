import "./Navbar.css";
import logo from "../assets/ktulogo.png";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";

function Navbar({ currentUser, backendStatus, onLogout, uploadSectionRef }) {
  const navigate = useNavigate();
  const location = useLocation();

  const [isDark, setIsDark] = useState(() => localStorage.getItem("theme") !== "light");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", isDark ? "dark" : "light");
    localStorage.setItem("theme", isDark ? "dark" : "light");
  }, [isDark]);

  const initials = currentUser ? currentUser.slice(0, 2).toUpperCase() : "?";

  const scrollToUpload = () => {
    if (location.pathname !== "/") {
      navigate("/");
      setTimeout(() => uploadSectionRef?.current?.scrollIntoView({ behavior: "smooth" }), 120);
    } else {
      uploadSectionRef?.current?.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <nav className="nav">
      <div className="nav-main">

        {/* ── LOGO ── */}
        <Link className="nav-logo" to="/">
          <div className="nav-logo-img-wrap">
            <img src={logo} alt="AISAT" className="nav-logo-img" />
            <div className="nav-logo-img-glow" />
          </div>
          <div className="nav-logo-divider" />
          <div className="nav-logo-text">
            <span className="logo-name">KTU Parser</span>
            <span className="logo-tagline">Result in seconds</span>
          </div>
        </Link>

        {/* ── NAV LINKS ── */}
        <div className="nav-links">
          <div className="nav-item">
            <button className="nav-link" onClick={scrollToUpload}>
              Upload
              <span className="nav-link-underline" />
            </button>
          </div>
          <div className="nav-item">
            <Link className="nav-link" to="/help">
              Help and FAQ
              <span className="nav-link-underline" />
            </Link>
          </div>
        </div>

        <div className="nav-spacer" />

        {/* ── RIGHT ── */}
        <div className="nav-actions">


          <div className="nav-divider" />

          <button className="btn-nav-cta" onClick={scrollToUpload}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="16 16 12 12 8 16" />
              <line x1="12" y1="12" x2="12" y2="21" />
              <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" />
            </svg>
            Upload PDF
          </button>

          <div className="nav-divider" />

          {/* User badge */}
          <div className="nav-user-badge">
            <div className="user-avatar">{initials}</div>
            <div className="user-info">
              <span className="user-name">{currentUser || "Account"}</span>
              <span className="user-role">Student</span>
            </div>
            <svg className="user-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="6 9 12 15 18 9" />
            </svg>

            <div className="user-dropdown">
              <div className="user-dropdown-header">
                <div className="user-avatar user-avatar--lg">{initials}</div>
                <div>
                  <div className="user-dropdown-name">{currentUser}</div>
                  <div className="user-dropdown-role">User</div>
                </div>
              </div>

              <div className="user-dropdown-divider" />

              <Link className="user-dropdown-item" to="/help">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                Help & FAQ
              </Link>

              <div className="user-dropdown-divider" />

              <div className="user-dropdown-item theme-toggle-row">
                <div className="theme-toggle-left">
                  {isDark ? (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                    </svg>
                  ) : (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="5"/>
                      <line x1="12" y1="1" x2="12" y2="3"/>
                      <line x1="12" y1="21" x2="12" y2="23"/>
                      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                      <line x1="1" y1="12" x2="3" y2="12"/>
                      <line x1="21" y1="12" x2="23" y2="12"/>
                      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                    </svg>
                  )}
                  {isDark ? "Dark mode" : "Light mode"}
                </div>
                <button
                  className={`theme-switch ${isDark ? "dark" : "light"}`}
                  onClick={() => setIsDark(v => !v)}
                  aria-label="Toggle theme"
                >
                  <div className="theme-switch-thumb">
                    {isDark ? (
                      <svg width="9" height="9" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                      </svg>
                    ) : (
                      <svg width="9" height="9" viewBox="0 0 24 24" fill="currentColor">
                        <circle cx="12" cy="12" r="5"/>
                      </svg>
                    )}
                  </div>
                </button>
              </div>

              <div className="user-dropdown-divider" />

              <button className="user-dropdown-item danger" onClick={onLogout}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                  <polyline points="16 17 21 12 16 7" />
                  <line x1="21" y1="12" x2="9" y2="12" />
                </svg>
                Sign Out
              </button>
            </div>
          </div>
        </div>

        <button className="nav-mobile-toggle" aria-label="Open menu">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="6"  x2="21" y2="6"  />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>

      </div>
    </nav>
  );
}

export default Navbar;