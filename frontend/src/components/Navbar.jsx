import "./Navbar.css";
import logo from "../assets/ktulogo.png";
import { Link, useNavigate, useLocation } from "react-router-dom";

const dropdownMenus = {
  Support: [
    {
      label: "HELP",
      items: [
        { icon: "💬", title: "Help Center", sub: "FAQs and guides", to: "/help" },
        { icon: "🐛", title: "Report Issue", sub: "Flag a parsing error" },
        { icon: "📬", title: "Contact Us",   sub: "Get in touch" },
      ],
    },
  ],
};

function Navbar({ currentUser, backendStatus, onLogout, uploadSectionRef }) {
  const statusLabel =
    backendStatus === "connected"
      ? "Our serivce is Online :)"
      : backendStatus === "disconnected"
      ? "API Offline"
      : "Connecting…";

  const initials = currentUser
    ? currentUser.slice(0, 2).toUpperCase()
    : "HI";

  const navigate   = useNavigate();
  const location   = useLocation();

  const scrollToUpload = () => {
    if (location.pathname !== "/") {
      // Navigate home first, then scroll after page loads
      navigate("/");
      setTimeout(() => {
        uploadSectionRef?.current?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } else {
      uploadSectionRef?.current?.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <nav className="nav">
      {/* ── TOP META BAR ── */}
      <div className="nav-meta">
        <div className={`nav-meta-status ${backendStatus}`}>
          <span className="status-dot"></span>
          {statusLabel}
        </div>

        <button className="nav-meta-link">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          </svg>
          v2.4.1
        </button>
      </div>

      {/* ── MAIN BAR ── */}
      <div className="nav-main">
        {/* LOGO */}
        <Link className="nav-logo" to="/">
          <img src={logo} alt="Logo" className="nav-logo-img" />
          <div className="nav-logo-text">
            <span className="logo-name">KTU Processor</span>
            <span className="logo-tagline">Result Intelligence</span>
          </div>
        </Link>

        {/* PRIMARY LINKS */}
        <div className="nav-links">


          {Object.entries(dropdownMenus).map(([label, sections]) => (
            <div className="nav-item" key={label}>
              <button className="nav-link">
                {label}
                <svg className="nav-link-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <polyline points="6 9 12 15 18 9" />
                </svg>
                <span className="nav-link-underline" />
              </button>

              <div className="nav-dropdown">
                {sections.map((section) => (
                  <div key={section.label}>
                    <div className="dropdown-section-label">{section.label}</div>
                    {section.items.map((item) =>
                      item.to ? (
                        <Link className="dropdown-link" to={item.to} key={item.title}>
                          <div className="dropdown-icon" style={{ background: "rgba(59,130,246,0.1)", fontSize: "1rem" }}>
                            {item.icon}
                          </div>
                          <span>
                            <span className="dropdown-link-text">{item.title}</span>
                            <span className="dropdown-link-sub">{item.sub}</span>
                          </span>
                        </Link>
                      ) : (
                        <button className="dropdown-link" key={item.title}>
                          <div className="dropdown-icon" style={{ background: "rgba(59,130,246,0.1)", fontSize: "1rem" }}>
                            {item.icon}
                          </div>
                          <span>
                            <span className="dropdown-link-text">{item.title}</span>
                            <span className="dropdown-link-sub">{item.sub}</span>
                          </span>
                        </button>
                      )
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="nav-spacer" />

        {/* RIGHT ACTIONS */}
        <div className="nav-actions">
          <div className="nav-divider" />

          <button className="btn-nav-cta" onClick={scrollToUpload}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="16 16 12 12 8 16" />
              <line x1="12" y1="12" x2="12" y2="21" />
              <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" />
            </svg>
            Upload PDF
          </button>

          <div className="nav-divider" />

          <div className="nav-user-badge">
            <div className="user-avatar">{initials}</div>
            <span className="user-name">{currentUser || "Account"}</span>
            <svg className="user-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="6 9 12 15 18 9" />
            </svg>

            <div className="user-dropdown">
              <div className="user-dropdown-header">
                <div className="user-dropdown-name">{currentUser}</div>
                <div className="user-dropdown-role">Meow</div>
              </div>

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

        <button className="nav-mobile-toggle">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>
      </div>
    </nav>
  );
}

export default Navbar;