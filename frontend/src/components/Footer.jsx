import "./Footer.css";

const footerLinks = {
  Product: [
    { label: "PDF Parser", badge: null },
    { label: "Excel Export", badge: null },
    { label: "Batch Processing", badge: "New" },
    { label: "Result Viewer", badge: null },
    { label: "API Access", badge: "Beta" },
    { label: "Changelog", badge: null },
  ],
  Developers: [
    { label: "REST API Docs", badge: null },
    { label: "Authentication", badge: null },
    { label: "Rate Limits", badge: null },
    { label: "SDKs", badge: "Beta" },
    { label: "Postman Collection", badge: null },
    { label: "Status Page", badge: null },
  ],
  Company: [
    { label: "About Us", badge: null },
    { label: "Blog", badge: null },
    { label: "Careers", badge: null },
    { label: "Press Kit", badge: null },
    { label: "Partners", badge: null },
    { label: "Security", badge: null },
  ],
};

function Footer() {
  return (
    <footer className="footer">
      {/* ── MAIN BODY ── */}
      <div className="footer-body">

        {/* Brand column */}
        <div className="footer-brand">
          <a className="footer-logo" href="#">
            <div className="footer-logo-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
              </svg>
            </div>
            <div className="footer-logo-text">
              <span className="footer-logo-name">KTU Processor</span>
              <span className="footer-logo-tag">Result Intelligence</span>
            </div>
          </a>

          <p className="footer-brand-desc">
            Automated KTU result PDF processing — parse, structure, and export
            student grade data to clean Excel reports in seconds. Built for
            institutions, admins, and developers.
          </p>

          <div className="footer-trust">
            <span className="trust-badge">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
              JWT Secured · Data encrypted in transit
            </span>
            <span className="trust-badge">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              KTU result format compatible
            </span>
          </div>

          <div className="footer-social">
            {/* GitHub */}
            <a className="social-btn" href="#" title="GitHub">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
              </svg>
            </a>
            {/* Twitter/X */}
            <a className="social-btn" href="#" title="Twitter">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z" />
              </svg>
            </a>
            {/* LinkedIn */}
            <a className="social-btn" href="#" title="LinkedIn">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
                <rect x="2" y="9" width="4" height="12" />
                <circle cx="4" cy="4" r="2" />
              </svg>
            </a>
            {/* Email */}
            <a className="social-btn" href="mailto:example@gmail.com" title="Email">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                <polyline points="22,6 12,13 2,6" />
              </svg>
            </a>
          </div>
        </div>

        {/* Link columns */}
        {Object.entries(footerLinks).map(([title, links]) => (
          <div className="footer-col" key={title}>
            <div className="footer-col-title">{title}</div>
            {links.map((link) => (
              <a className="footer-link" href="#" key={link.label}>
                {link.label}
                {link.badge && (
                  <span className={`link-badge ${link.badge === "New" ? "new" : ""}`}>
                    {link.badge}
                  </span>
                )}
              </a>
            ))}
          </div>
        ))}

        {/* Contact column */}
        <div className="footer-col">
          <div className="footer-col-title">Contact</div>

          <div className="footer-contact-item">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
              <polyline points="22,6 12,13 2,6" />
            </svg>
            <a href="mailto:example@gmail.com">example@gmail.com</a>
          </div>

          <div className="footer-contact-item">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
            <span>Support: Mon–Fri, 9am–6pm IST</span>
          </div>

          <div className="footer-contact-item">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
              <circle cx="12" cy="10" r="3" />
            </svg>
            <span>Kerala, India</span>
          </div>

          {/* API status mini-card */}
          <div style={{
            marginTop: "0.75rem",
            padding: "0.75rem",
            background: "rgba(52, 211, 153, 0.05)",
            border: "1px solid rgba(52, 211, 153, 0.15)",
            borderRadius: "8px",
            display: "flex",
            flexDirection: "column",
            gap: "0.35rem"
          }}>
            <div style={{ fontSize: "0.65rem", fontWeight: 600, color: "rgba(255,255,255,0.25)", letterSpacing: "0.1em", textTransform: "uppercase" }}>
              System Status
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.775rem", color: "#34d399" }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#34d399", boxShadow: "0 0 6px rgba(52,211,153,0.6)", display: "inline-block", flexShrink: 0 }}></span>
              All systems operational
            </div>
            <div style={{ fontSize: "0.725rem", color: "rgba(255,255,255,0.25)" }}>
              API · Parser · Export Engine
            </div>
          </div>
        </div>
      </div>

      <div className="footer-divider" />

      {/* ── BOTTOM BAR ── */}
      <div className="footer-bottom">
        <div className="footer-copyright">
          © 2026 <strong>KTU Processor</strong>. All Rights Reserved.
          &nbsp;·&nbsp; Built with FastAPI + React &nbsp;·&nbsp; Made in Kerala 🇮🇳
        </div>

        <div className="footer-bottom-links">
          <button className="footer-bottom-link">Privacy Policy</button>
          <span className="footer-bottom-sep" />
          <button className="footer-bottom-link">Terms of Service</button>
          <span className="footer-bottom-sep" />
          <button className="footer-bottom-link">Cookie Policy</button>
          <span className="footer-bottom-sep" />
          <button className="footer-bottom-link">GDPR</button>
          <span className="footer-bottom-sep" />
          <button className="footer-bottom-link">Accessibility</button>
        </div>

        <div className="footer-version">
          <span className="version-dot" />
          v2.4.1 stable
        </div>
      </div>
    </footer>
  );
}

export default Footer;