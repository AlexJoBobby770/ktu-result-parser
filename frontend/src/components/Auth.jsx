import "./Auth.css";
import logo from "../assets/ktulogo.png";
import { useState } from "react";
import { auth, googleProvider } from "../firebase";
import { signInWithPopup } from "firebase/auth";

function Auth({ onLogin }) {
  const [mode, setMode]       = useState("login"); // "login" | "register"
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm]   = useState("");
  const [showPass, setShowPass] = useState(false);
  const [error, setError]       = useState("");
  const [loading, setLoading]   = useState(false);
  const [gLoading, setGLoading] = useState(false);

  const switchMode = (m) => {
    setMode(m);
    setError("");
    setUsername("");
    setPassword("");
    setConfirm("");
  };

  /* ── Google Sign-In ── */
  const handleGoogle = async () => {
    setError("");
    setGLoading(true);
    try {
      const result = await signInWithPopup(auth, googleProvider);
      onLogin(result.user.displayName || result.user.email);
    } catch (err) {
      if (err.code !== "auth/popup-closed-by-user") {
        setError(err.code === "auth/network-request-failed"
          ? "Network error. Check your connection."
          : err.message || "Google sign-in failed.");
      }
    } finally {
      setGLoading(false);
    }
  };

  /* ── Email/Password ── */
  const handleSubmit = async () => {
    setError("");
    if (!username.trim() || !password.trim()) {
      setError("Please fill in all fields.");
      return;
    }
    if (mode === "register") {
      if (password !== confirm) { setError("Passwords do not match."); return; }
      if (password.length < 6)  { setError("Password must be at least 6 characters."); return; }
    }
    setLoading(true);
    try {
      const endpoint = mode === "login" ? "/api/auth/login" : "/api/auth/register";
      const res  = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username.trim(), password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Something went wrong.");
      onLogin(data.username || username.trim());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => { if (e.key === "Enter") handleSubmit(); };

  return (
    <div className="auth-root">

      {/* ══ LEFT PANEL ══ */}
      <div className="auth-panel auth-panel--left">
        <div className="auth-bg-grid" aria-hidden />
        <div className="auth-bg-orb auth-bg-orb--1" aria-hidden />
        <div className="auth-bg-orb auth-bg-orb--2" aria-hidden />
        <div className="auth-bg-orb auth-bg-orb--3" aria-hidden />

        <div className="auth-left-content">

          <div className="auth-institution-badge">
            <span className="auth-badge-dot" />
            KTU Affiliated Institution
          </div>

          <div className="auth-logo-cathedral">
            <div className="auth-logo-ring auth-logo-ring--3" aria-hidden />
            <div className="auth-logo-ring auth-logo-ring--2" aria-hidden />
            <div className="auth-logo-ring auth-logo-ring--1" aria-hidden />
            <div className="auth-logo-glow-floor" aria-hidden />
            <img src={logo} alt="AISAT College of Engineering" className="auth-logo-img" />
          </div>

          <div className="auth-left-title">
            <h1 className="auth-college-name">AISAT College of<br />Engineering</h1>
            <p className="auth-college-location">Ernakulam, Kerala</p>
          </div>

          <div className="auth-app-descriptor">
            <div className="auth-descriptor-line" />
            <div className="auth-descriptor-text">
              <span className="auth-descriptor-label">KTU Result Parser</span>
              <span className="auth-descriptor-sub">Instant academic result analysis</span>
            </div>
          </div>

          <div className="auth-feature-pills">
            <span className="auth-pill">⚡ Instant PDF parsing</span>
            <span className="auth-pill">📊 SGPA &amp; CGPA calc</span>
            <span className="auth-pill">🔒 Secure &amp; private</span>
          </div>

        </div>
      </div>

      {/* ══ RIGHT PANEL ══ */}
      <div className="auth-panel auth-panel--right">
        <div className="auth-form-wrap">

          {/* Mobile logo */}
          <div className="auth-mobile-logo">
            <img src={logo} alt="AISAT" className="auth-mobile-logo-img" />
            <span className="auth-mobile-logo-name">KTU Result Parser</span>
          </div>

          {/* Tab switcher */}
          <div className="auth-tabs">
            <button className={`auth-tab ${mode === "login" ? "auth-tab--active" : ""}`} onClick={() => switchMode("login")}>Sign In</button>
            <button className={`auth-tab ${mode === "register" ? "auth-tab--active" : ""}`} onClick={() => switchMode("register")}>Register</button>
            <div className={`auth-tab-indicator ${mode === "register" ? "auth-tab-indicator--right" : ""}`} />
          </div>

          {/* Heading */}
          <div className="auth-form-header">
            <h2 className="auth-form-title">
              {mode === "login" ? "Welcome back" : "Create account"}
            </h2>
            <p className="auth-form-sub">
              {mode === "login" ? "Sign in to access your result dashboard" : "Register to start parsing KTU results"}
            </p>
          </div>

          {/* Google button */}
          <button
            className={`auth-google-btn ${gLoading ? "auth-google-btn--loading" : ""}`}
            onClick={handleGoogle}
            disabled={gLoading || loading}
          >
            {gLoading ? (
              <><span className="auth-spinner auth-spinner--dark" /> Signing in…</>
            ) : (
              <>
                <svg className="auth-google-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                Continue with Google
              </>
            )}
          </button>

          {/* Divider */}
          <div className="auth-divider">
            <span className="auth-divider-line" />
            <span className="auth-divider-text">or continue with username</span>
            <span className="auth-divider-line" />
          </div>

          {/* Error */}
          {error && (
            <div className="auth-error" role="alert">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              {error}
            </div>
          )}

          {/* Fields */}
          <div className="auth-fields">
            <div className="auth-field">
              <label className="auth-label" htmlFor="auth-username">Username</label>
              <div className="auth-input-wrap">
                <svg className="auth-input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
                <input
                  id="auth-username"
                  type="text"
                  className="auth-input"
                  placeholder="Enter your username"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  onKeyDown={handleKey}
                  autoComplete="username"
                />
              </div>
            </div>

            <div className="auth-field">
              <label className="auth-label" htmlFor="auth-password">Password</label>
              <div className="auth-input-wrap">
                <svg className="auth-input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                <input
                  id="auth-password"
                  type={showPass ? "text" : "password"}
                  className="auth-input"
                  placeholder="Enter your password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  onKeyDown={handleKey}
                  autoComplete={mode === "login" ? "current-password" : "new-password"}
                />
                <button className="auth-input-eye" onClick={() => setShowPass(v => !v)} type="button" aria-label="Toggle password">
                  {showPass ? (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                      <line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                  ) : (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {mode === "register" && (
              <div className="auth-field auth-field--animated">
                <label className="auth-label" htmlFor="auth-confirm">Confirm Password</label>
                <div className="auth-input-wrap">
                  <svg className="auth-input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                  <input
                    id="auth-confirm"
                    type={showPass ? "text" : "password"}
                    className="auth-input"
                    placeholder="Repeat your password"
                    value={confirm}
                    onChange={e => setConfirm(e.target.value)}
                    onKeyDown={handleKey}
                    autoComplete="new-password"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Submit */}
          <button
            className={`auth-submit ${loading ? "auth-submit--loading" : ""}`}
            onClick={handleSubmit}
            disabled={loading || gLoading}
          >
            {loading ? (
              <><span className="auth-spinner" />{mode === "login" ? "Signing in…" : "Creating account…"}</>
            ) : (
              <>
                {mode === "login" ? "Sign In" : "Create Account"}
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <line x1="5" y1="12" x2="19" y2="12"/>
                  <polyline points="12 5 19 12 12 19"/>
                </svg>
              </>
            )}
          </button>

          {/* Switch */}
          <p className="auth-switch">
            {mode === "login" ? "Don't have an account? " : "Already have an account? "}
            <button className="auth-switch-link" onClick={() => switchMode(mode === "login" ? "register" : "login")}>
              {mode === "login" ? "Register here" : "Sign in"}
            </button>
          </p>

          {/* Footer */}
          <div className="auth-footer-note">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            Your data is stored securely and never shared.
          </div>

        </div>
      </div>
    </div>
  );
}

export default Auth;