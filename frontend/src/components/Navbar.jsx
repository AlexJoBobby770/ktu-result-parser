import "./Navbar.css";
import logo from "../assets/ktulogo.png";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useState, useEffect, useRef } from "react";

function Navbar({ currentUser, backendStatus, onLogout, uploadSectionRef }) {
  const navigate = useNavigate();
  const location = useLocation();

  const [scrolled, setScrolled]       = useState(false);
  const [dropdownOpen, setDropdown]   = useState(false);
  const [mobileOpen, setMobile]       = useState(false);
  const dropdownRef                   = useRef(null);

  /* ── scroll shadow ── */
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  /* ── close dropdown on outside click ── */
  useEffect(() => {
    const onOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target))
        setDropdown(false);
    };
    document.addEventListener("mousedown", onOutside);
    return () => document.removeEventListener("mousedown", onOutside);
  }, []);

  /* ── close mobile drawer on route change ── */
  useEffect(() => setMobile(false), [location.pathname]);

  const initials = currentUser
    ? currentUser.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase()
    : "U";

  const scrollToUpload = () => {
    setMobile(false);
    if (location.pathname !== "/") {
      navigate("/");
      setTimeout(() => uploadSectionRef?.current?.scrollIntoView({ behavior: "smooth" }), 130);
    } else {
      uploadSectionRef?.current?.scrollIntoView({ behavior: "smooth" });
    }
  };

  const isLive = backendStatus === "connected";

  return (
    <>
      {/* ══════════════════════════════════════ NAVBAR ══════════════════════════════════════ */}
      <header className={`nb${scrolled ? " nb--raised" : ""}`}>
        <div className="nb__wrap">

          {/* ─── Logo ─────────────────────────────────────────── */}
          <Link to="/" className="nb__logo">
            <div className="nb__logo-img-box">
              <img src={logo} alt="AISAT" className="nb__logo-img" />
            </div>
            <div className="nb__logo-sep" />
            <div className="nb__logo-copy">
              <span className="nb__logo-product">KTU Result Parser</span>
              <span className="nb__logo-sub">Result within seconds</span>
            </div>
          </Link>

          {/* ─── Desktop nav links ────────────────────────────── */}
          <nav className="nb__links">
            <button className="nb__link" onClick={scrollToUpload}>Upload</button>
            <Link   className="nb__link" to="/help">Help &amp; FAQ</Link>
          </nav>

          {/* ─── Right-side cluster ───────────────────────────── */}
          <div className="nb__right">

            {/* Backend status pill */}
            <div className={`nb__pill${isLive ? " nb__pill--live" : " nb__pill--off"}`}>
              <span className="nb__pill-dot" />
              {isLive ? "API Live" : "Offline"}
            </div>

            {/* Primary CTA */}
            <button className="nb__cta" onClick={scrollToUpload}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <polyline points="16 16 12 12 8 16" />
                <line x1="12" y1="12" x2="12" y2="21" />
                <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" />
              </svg>
              Upload PDF
            </button>

            {/* User avatar + dropdown */}
            <div className="nb__user" ref={dropdownRef}>
              <button
                className="nb__avatar-btn"
                onClick={() => setDropdown((v) => !v)}
                aria-expanded={dropdownOpen}
                aria-label="Account"
              >
                <span className="nb__avatar">{initials}</span>
                <svg
                  className={`nb__chevron${dropdownOpen ? " nb__chevron--up" : ""}`}
                  width="11" height="11" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"
                >
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </button>

              {/* Dropdown panel */}
              <div className={`nb__drop${dropdownOpen ? " nb__drop--open" : ""}`}>
                <div className="nb__drop-head">
                  <div className="nb__drop-avatar">{initials}</div>
                  <div className="nb__drop-info">
                    <p className="nb__drop-name">{currentUser || "Account"}</p>
                    <p className="nb__drop-role">Faculty Member</p>
                  </div>
                </div>

                <div className="nb__drop-divider" />

                <Link
                  className="nb__drop-item"
                  to="/help"
                  onClick={() => setDropdown(false)}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                       stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                    <line x1="12" y1="17" x2="12.01" y2="17" />
                  </svg>
                  Help &amp; FAQ
                </Link>

                <button
                  className="nb__drop-item nb__drop-item--danger"
                  onClick={() => { setDropdown(false); onLogout(); }}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                       stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                    <polyline points="16 17 21 12 16 7" />
                    <line x1="21" y1="12" x2="9" y2="12" />
                  </svg>
                  Sign Out
                </button>
              </div>
            </div>
          </div>

          {/* ─── Mobile hamburger ─────────────────────────────── */}
          <button
            className={`nb__burger${mobileOpen ? " nb__burger--open" : ""}`}
            onClick={() => setMobile((v) => !v)}
            aria-label="Toggle menu"
          >
            <span /><span /><span />
          </button>
        </div>

        {/* ══ Mobile slide-down drawer ══ */}
        <div className={`nb__drawer${mobileOpen ? " nb__drawer--open" : ""}`}>
          <div className="nb__drawer-user">
            <div className="nb__drop-avatar" style={{ width: 40, height: 40 }}>{initials}</div>
            <div>
              <p className="nb__drop-name">{currentUser || "Account"}</p>
              <p className="nb__drop-role">Faculty Member</p>
            </div>
          </div>

          <div className="nb__drawer-divider" />

          <button className="nb__drawer-link" onClick={scrollToUpload}>Upload</button>
          <Link   className="nb__drawer-link" to="/help">Help &amp; FAQ</Link>

          <div className="nb__drawer-divider" />

          <button className="nb__drawer-cta"     onClick={scrollToUpload}>Upload PDF</button>
          <button className="nb__drawer-signout" onClick={() => { setMobile(false); onLogout(); }}>
            Sign Out
          </button>
        </div>
      </header>

      {/* Spacer so page content starts below the fixed bar */}
      <div className="nb__spacer" />
    </>
  );
}

export default Navbar;