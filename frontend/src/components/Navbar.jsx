import "./Navbar.css";
import logo from "../assets/ktulogo.png";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useState, useEffect, useRef } from "react";

function Navbar({ currentUser, backendStatus, onLogout, uploadSectionRef }) {
  const navigate   = useNavigate();
  const location   = useLocation();
  const [elevated, setElevated]   = useState(false);
  const [dropOpen, setDropOpen]   = useState(false);
  const [menuOpen, setMenuOpen]   = useState(false);
  const dropRef = useRef(null);

  /* Elevate on scroll */
  useEffect(() => {
    const fn = () => setElevated(window.scrollY > 6);
    window.addEventListener("scroll", fn, { passive: true });
    return () => window.removeEventListener("scroll", fn);
  }, []);

  /* Close dropdown on outside click */
  useEffect(() => {
    const fn = (e) => {
      if (dropRef.current && !dropRef.current.contains(e.target))
        setDropOpen(false);
    };
    document.addEventListener("mousedown", fn);
    return () => document.removeEventListener("mousedown", fn);
  }, []);

  /* Close drawer on route change */
  useEffect(() => { setMenuOpen(false); }, [location.pathname]);

  /* Build initials from display name */
  const initials = currentUser
    ? currentUser.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase()
    : "U";

  const scrollToUpload = () => {
    setMenuOpen(false);
    if (location.pathname !== "/") {
      navigate("/");
      setTimeout(
        () => uploadSectionRef?.current?.scrollIntoView({ behavior: "smooth" }),
        150
      );
    } else {
      uploadSectionRef?.current?.scrollIntoView({ behavior: "smooth" });
    }
  };


  return (
    <>
      <header className={`nb${elevated ? " nb--elevated" : ""}`}>
        <div className="nb__rail">

          {/* ════ BRAND ════ */}
          <Link to="/" className="nb__brand">
            {/* Logo — large, anchored, clearly visible */}
            <div className="nb__logo-frame">
              <img src={logo} alt="AISAT" className="nb__logo-img" />
            </div>

            {/* Divider */}
            <div className="nb__brand-sep" aria-hidden="true" />

            {/* Title — short and strong */}
            <div className="nb__brand-copy">
              <span className="nb__brand-title">Result&nbsp;Portal</span>
              <span className="nb__brand-college">AISAT · Ernakulam</span>
            </div>
          </Link>

          {/* ════ NAV LINKS ════ */}
          <nav className="nb__nav" aria-label="Primary navigation">
            <button className="nb__nav-link" onClick={scrollToUpload}>
              Upload
            </button>
            <Link className="nb__nav-link" to="/help">
              Help
            </Link>
          </nav>

          {/* ════ RIGHT CLUSTER ════ */}
          <div className="nb__end">


            {/* Upload CTA */}
            <button className="nb__cta" onClick={scrollToUpload}>
              Upload PDF
              <svg
                width="12" height="12" viewBox="0 0 24 24"
                fill="none" stroke="currentColor"
                strokeWidth="2.5" strokeLinecap="round"
              >
                <line x1="5" y1="12" x2="19" y2="12" />
                <polyline points="12 5 19 12 12 19" />
              </svg>
            </button>

            {/* Avatar dropdown */}
            <div className="nb__user" ref={dropRef}>
              <button
                className="nb__avatar-btn"
                onClick={() => setDropOpen((v) => !v)}
                aria-expanded={dropOpen}
                aria-haspopup="true"
                aria-label="Account menu"
              >
                <span className="nb__avatar">{initials}</span>
                <svg
                  className={`nb__avatar-chevron${dropOpen ? " nb__avatar-chevron--open" : ""}`}
                  width="11" height="11" viewBox="0 0 24 24"
                  fill="none" stroke="currentColor"
                  strokeWidth="2.5" strokeLinecap="round"
                >
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </button>

              {/* Dropdown panel */}
              <div
                className={`nb__drop${dropOpen ? " nb__drop--open" : ""}`}
                role="menu"
              >
                {/* Header */}
                <div className="nb__drop-head">
                  <div className="nb__drop-avatar">{initials}</div>
                  <div className="nb__drop-info">
                    <p className="nb__drop-name">{currentUser || "Account"}</p>
                    <p className="nb__drop-role">Faculty Member</p>
                  </div>
                </div>

                <div className="nb__drop-rule" />

                <Link
                  to="/help"
                  className="nb__drop-item"
                  role="menuitem"
                  onClick={() => setDropOpen(false)}
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
                  role="menuitem"
                  onClick={() => { setDropOpen(false); onLogout(); }}
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

          {/* ════ HAMBURGER ════ */}
          <button
            className={`nb__burger${menuOpen ? " nb__burger--open" : ""}`}
            onClick={() => setMenuOpen((v) => !v)}
            aria-label={menuOpen ? "Close menu" : "Open menu"}
            aria-expanded={menuOpen}
          >
            <span /><span /><span />
          </button>
        </div>

        {/* ════ MOBILE DRAWER ════ */}
        <div
          className={`nb__drawer${menuOpen ? " nb__drawer--open" : ""}`}
          aria-hidden={!menuOpen}
        >
          <div className="nb__drawer-user">
            <div className="nb__drop-avatar" style={{ width: 42, height: 42, fontSize: "0.85rem" }}>
              {initials}
            </div>
            <div>
              <p className="nb__drop-name">{currentUser}</p>
              <p className="nb__drop-role">Faculty Member</p>
            </div>
          </div>

          <div className="nb__drawer-rule" />

          <button className="nb__drawer-link" onClick={scrollToUpload}>
            Upload
          </button>
          <Link className="nb__drawer-link" to="/help">
            Help &amp; FAQ
          </Link>

          <div className="nb__drawer-rule" />

          <button className="nb__drawer-cta" onClick={scrollToUpload}>
            Upload PDF
          </button>
          <button
            className="nb__drawer-signout"
            onClick={() => { setMenuOpen(false); onLogout(); }}
          >
            Sign Out
          </button>
        </div>
      </header>

      {/* Spacer so page content clears the fixed bar */}
      <div className="nb__spacer" aria-hidden="true" />
    </>
  );
}

export default Navbar;