import { useState, useEffect } from "react";
import "./Auth.css";
import logo from "../assets/ktulogo.png";
import { signInWithPopup, GoogleAuthProvider } from "firebase/auth";
import { auth } from "../firebase";
const STARS = Array.from({ length: 80 }, (_, i) => ({
  id: i,
  top: `${Math.random() * 100}%`,
  left: `${Math.random() * 100}%`,
  size: Math.random() * 2.2 + 0.3,
  dur: `${(Math.random() * 5 + 3).toFixed(1)}s`,
  delay: `${(Math.random() * 8).toFixed(1)}s`,
  op: (Math.random() * 0.5 + 0.15).toFixed(2),
}));
const STREAM = [
  { mod: "INGEST", msg: "PDF validated — 4 pages", ok: true },
  { mod: "EXTRACT", msg: "2,847 tokens extracted", ok: true },
  { mod: "PARSE", msg: "12 subjects detected", ok: true },
  { mod: "COMPILE", msg: "6 columns mapped", ok: true },
  { mod: "EXPORT", msg: "results.xlsx ready", ok: true },
];
const FEATURES = [
  { icon: "⚡", text: "0.8s avg parse" },
  { icon: "📊", text: "100% accuracy" },
  { icon: "🔒", text: "Zero retention" },
  { icon: "🚀", text: "Auto-grading" },
];
export default function Auth({ onAuthSuccess }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);
  const handleGoogle = async () => {
    setError("");
    setLoading(true);
    try {
      const provider = new GoogleAuthProvider();
      const result = await signInWithPopup(auth, provider);
      onAuthSuccess(result.user);
    } catch (err) {
      if (err.code === "auth/popup-closed-by-user") {
      } else if (err.code === "auth/network-request-failed") {
        setError("Network error. Check your connection.");
      } else {
        setError("Sign-in failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="auth-root">
      <div className="auth-bg-noise" aria-hidden />
      {/* ════════════════════════════ LEFT PANEL ════════════════════ */}
      <div className="auth-left">
        <div className="auth-stars" aria-hidden>
          {STARS.map((s) => (
            <span
              key={s.id}
              className="auth-star"
              style={{
                top: s.top,
                left: s.left,
                width: s.size + "px",
                height: s.size + "px",
                "--dur": s.dur,
                "--delay": s.delay,
                "--op": s.op,
              }}
            />
          ))}
        </div>
        <div className="auth-aurora" aria-hidden>
          <div className="auth-aurora-1" />
          <div className="auth-aurora-2" />
          <div className="auth-aurora-3" />
          <div className="auth-aurora-4" />
        </div>
        <div className="auth-grid" aria-hidden />
        <div className="auth-glow-spot" style={{
          "--x": mousePos.x + "px",
          "--y": mousePos.y + "px",
        }} aria-hidden />
        <div className="auth-left-content">
          <div className="auth-ktu-badge">
            <span className="auth-ktu-dot" />
            <span>APJ Abdul Kalam Technological University</span>
          </div>
          <div className="auth-logo-stage">
            <div className="auth-ring auth-ring--a" aria-hidden />
            <div className="auth-ring auth-ring--b" aria-hidden />
            <div className="auth-ring auth-ring--c" aria-hidden />
            <div className="auth-ring auth-ring--d" aria-hidden />
            <div className="auth-logo-floor" aria-hidden />
            <div className="auth-logo-halo" aria-hidden />
            <div className="auth-logo-inner-glow" aria-hidden />
            <img src={logo} alt="AISAT" className="auth-logo-img" />
          </div>
          <div className="auth-college-name">
            <h1 className="auth-name-main">AISAT</h1>
            <p className="auth-name-sub">College of Engineering</p>
            <span className="auth-name-loc">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" />
                <circle cx="12" cy="9" r="2.5" />
              </svg>
              Ernakulam, Kerala
            </span>
          </div>
          <div className="auth-viz">
            <div className="auth-viz-bar">
              <span className="auth-viz-dot-live" />
              <span className="auth-viz-bar-title">pipeline.live</span>
              <span className="auth-viz-bar-status">RUNNING</span>
            </div>
            <div className="auth-viz-stream">
              {[...STREAM, ...STREAM].map((line, i) => (
                <div
                  key={i}
                  className="auth-stream-row"
                  style={{ "--i": i % STREAM.length }}
                >
                  <span className="auth-stream-mod">[{line.mod}]</span>
                  <span className="auth-stream-msg">{line.msg}</span>
                  <span className="auth-stream-ok">OK</span>
                </div>
              ))}
              <div className="auth-viz-fade" aria-hidden />
            </div>
          </div>
          <div className="auth-left-pills">
            {FEATURES.map((f, i) => (
              <span key={i} className="auth-left-pill">
                {f.icon} {f.text}
              </span>
            ))}
          </div>
          <div className="auth-stats">
            <div className="auth-stat">
              <span className="auth-stat-value">50K+</span>
              <span className="auth-stat-label">Results Processed</span>
            </div>
            <div className="auth-stat-divider" />
            <div className="auth-stat">
              <span className="auth-stat-value">99.9%</span>
              <span className="auth-stat-label">Uptime</span>
            </div>
            <div className="auth-stat-divider" />
            <div className="auth-stat">
              <span className="auth-stat-value">24/7</span>
              <span className="auth-stat-label">Active</span>
            </div>
          </div>
        </div>
      </div>
      {/* ════════════════════════════ RIGHT PANEL ════════════════════ */}
      <div className="auth-right">
        <div className="auth-right-inner">
          <div className="auth-right-eyebrow">
            <span className="auth-right-eyebrow-line" />
            <span>Secure Access</span>
            <span className="auth-right-eyebrow-line" />
          </div>
          <div className="auth-right-heading">
            <h2 className="auth-right-title">Welcome back</h2>
            <p className="auth-right-sub">
              Sign in to start processing KTU result PDFs into structured Excel reports.
            </p>
          </div>
          {error && (
            <div className="auth-error" role="alert">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              {error}
            </div>
          )}
          <button
            className={`auth-google-btn ${loading ? "auth-google-btn--busy" : ""}`}
            onClick={handleGoogle}
            disabled={loading}
          >
            <span className="auth-google-btn-bg" aria-hidden />
            <span className="auth-google-btn-shimmer" aria-hidden />
            <span className="auth-google-btn-inner">
              {loading ? (
                <>
                  <span className="auth-google-spinner" />
                  <span>Signing you in…</span>
                </>
              ) : (
                <>
                  <svg className="auth-glogo" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05" />
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                  </svg>
                  <span>Continue with Google</span>
                  <svg className="auth-google-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <line x1="5" y1="12" x2="19" y2="12" />
                    <polyline points="12 5 19 12 12 19" />
                  </svg>
                </>
              )}
            </span>
          </button>
          <div className="auth-divider">
            <span />
            <span className="auth-divider-text">Powered by Firebase Auth</span>
            <span />
          </div>
          <div className="auth-trust-grid">
            <div className="auth-trust-item">
              <div className="auth-trust-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
              </div>
              <div>
                <div className="auth-trust-label">Firebase Protected</div>
                <div className="auth-trust-sub">OAuth 2.0</div>
              </div>
            </div>
            <div className="auth-trust-item">
              <div className="auth-trust-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
              </div>
              <div>
                <div className="auth-trust-label">AES-256 Encrypted</div>
                <div className="auth-trust-sub">End-to-end</div>
              </div>
            </div>
            <div className="auth-trust-item">
              <div className="auth-trust-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="1 4 1 10 7 10" />
                  <path d="M3.51 15a9 9 0 1 0 .49-3.29" />
                </svg>
              </div>
              <div>
                <div className="auth-trust-label">Zero Retention</div>
                <div className="auth-trust-sub">Files never stored</div>
              </div>
            </div>
            <div className="auth-trust-item">
              <div className="auth-trust-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                </svg>
              </div>
              <div>
                <div className="auth-trust-label">Live Pipeline</div>
                <div className="auth-trust-sub">5-stage processing</div>
              </div>
            </div>
          </div>
          <p className="auth-footnote">
            By continuing, you agree to our terms of use.
            <br />
            Only your name &amp; email are accessed.
          </p>
          <div className="auth-version">
            <span className="auth-version-dot" /> v1.0.0
          </div>
        </div>
      </div>
    </div>
  );
}