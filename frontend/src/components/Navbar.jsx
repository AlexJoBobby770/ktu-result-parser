import "./Navbar.css";

const dropdownMenus = {
  Products: [
    {
      label: "CORE TOOLS",
      items: [
        { icon: "📄", title: "PDF Parser", sub: "Upload & process KTU results", emoji: true },
        { icon: "📊", title: "Excel Export", sub: "Structured data download", emoji: true },
        { icon: "🔍", title: "Result Viewer", sub: "Browse parsed records", emoji: true },
      ],
    },
    {
      label: "ANALYTICS",
      items: [
        { icon: "📈", title: "Score Reports", sub: "Grade distribution charts", emoji: true },
        { icon: "🏛️", title: "Batch Compare", sub: "Multi-semester analysis", emoji: true },
      ],
    },
  ],
  Developers: [
    {
      label: "RESOURCES",
      items: [
        { icon: "🔌", title: "REST API", sub: "Integrate with your systems", emoji: true },
        { icon: "📚", title: "Documentation", sub: "Guides & references", emoji: true },
        { icon: "⚡", title: "API Keys", sub: "Manage access tokens", emoji: true },
      ],
    },
  ],
  Support: [
    {
      label: "HELP",
      items: [
        { icon: "💬", title: "Help Center", sub: "FAQs and guides", emoji: true },
        { icon: "🐛", title: "Report Issue", sub: "Flag a parsing error", emoji: true },
        { icon: "📬", title: "Contact Us", sub: "Get in touch", emoji: true },
      ],
    },
  ],
};

function Navbar({ currentUser, backendStatus, onLogout, uploadSectionRef }) {
  const statusLabel =
    backendStatus === "connected"
      ? "API Online"
      : backendStatus === "disconnected"
      ? "API Offline"
      : "Connecting…";

  const initials = currentUser
    ? currentUser.slice(0, 2).toUpperCase()
    : "KP";

  const scrollToUpload = () => {
    uploadSectionRef?.current?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <nav className="nav">
      {/* ── TOP META BAR ── */}
      <div className="nav-meta">
        <div className={`nav-meta-status ${backendStatus}`}>
          <span className="status-dot"></span>
          {statusLabel}
        </div>

        <div className="nav-meta-divider" />

        <button className="nav-meta-link">What's New</button>
        <button className="nav-meta-link">Changelog</button>
        <button className="nav-meta-link">System Status</button>

        <div className="nav-meta-divider" />

        <button className="nav-meta-link">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 8v4l3 3" />
          </svg>
          v2.4.1
        </button>
      </div>

      {/* ── MAIN BAR ── */}
      <div className="nav-main">
        {/* LOGO */}
        <a className="nav-logo" href="#">
          <div className="nav-logo-icon">
            <div className="logo-ring">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
              </svg>
            </div>
          </div>
          <div className="nav-logo-text">
            <span className="logo-name">KTU Processor</span>
            <span className="logo-tagline">Result Intelligence</span>
          </div>
        </a>

        {/* PRIMARY LINKS */}
        <div className="nav-links">
          {/* Plain link */}
          <div className="nav-item">
            <button className="nav-link" onClick={scrollToUpload}>
              Upload
              <span className="nav-link-underline" />
            </button>
          </div>

          {/* Dropdown links */}
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
                    {section.items.map((item) => (
                      <button className="dropdown-link" key={item.title}>
                        <div
                          className="dropdown-icon"
                          style={{ background: "rgba(59,130,246,0.1)", fontSize: "1rem" }}
                        >
                          {item.icon}
                        </div>
                        <span>
                          <span className="dropdown-link-text">{item.title}</span>
                          <span className="dropdown-link-sub">{item.sub}</span>
                        </span>
                      </button>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          ))}

          <div className="nav-item">
            <button className="nav-link">
              Pricing
              <span className="nav-link-underline" />
            </button>
          </div>
        </div>

        <div className="nav-spacer" />

        {/* RIGHT ACTIONS */}
        <div className="nav-actions">
          {/* Search */}
          <button className="nav-search-btn" title="Search">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
          </button>

          <div className="nav-divider" />

          {/* Upload CTA */}
          <button className="btn-nav-cta" onClick={scrollToUpload}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
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
            <span className="user-name">{currentUser || "Account"}</span>
            <svg className="user-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="6 9 12 15 18 9" />
            </svg>

            {/* User dropdown */}
            <div className="user-dropdown">
              <div className="user-dropdown-header">
                <div className="user-dropdown-name">{currentUser}</div>
                <div className="user-dropdown-role">Free Plan · KTU Processor</div>
              </div>

              <button className="user-dropdown-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
                My Profile
              </button>
              <button className="user-dropdown-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 20h9" />
                  <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                </svg>
                Upload History
              </button>
              <button className="user-dropdown-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="3" />
                  <path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14" />
                </svg>
                Settings
              </button>

              <div className="user-dropdown-separator" />

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

        {/* Mobile toggle */}
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