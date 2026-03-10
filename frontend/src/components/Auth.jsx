import "./Auth.css";
import logo from "../assets/ktulogo.png";
import { useState } from "react";
import { auth, googleProvider } from "../firebase";
import { signInWithPopup } from "firebase/auth";

function Auth({ onLogin }) {
  const [error, setError]     = useState("");
  const [loading, setLoading] = useState(false);

  const handleGoogle = async () => {
    setError("");
    setLoading(true);
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const user   = result.user;
      onLogin(user.displayName || user.email);
    } catch (err) {
      if (err.code === "auth/popup-closed-by-user") {
        // user dismissed — silent
      } else if (err.code === "auth/network-request-failed") {
        setError("Network error. Check your connection and try again.");
      } else {
        setError(err.message || "Sign-in failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-root">

      {/* ══ LEFT PANEL — logo cathedral ══ */}
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
            <img
              src={logo}
              alt="AISAT College of Engineering"
              className="auth-logo-img"
            />
          </div>

          <div className="auth-left-title">
            <h1 className="auth-college-name">
              AISAT College of<br />Engineering
            </h1>
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
            <span className="auth-pill">📊 GPA &amp; CGPA calc</span>
            <span className="auth-pill">🔒 Secure &amp; private</span>
          </div>

        </div>
      </div>

      {/* ══ RIGHT PANEL — sign in ══ */}
      <div className="auth-panel auth-panel--right">
        <div className="auth-form-wrap">

          {/* Mobile logo */}
          <div className="auth-mobile-logo">
            <img src={logo} alt="AISAT" className="auth-mobile-logo-img" />
            <span className="auth-mobile-logo-name">KTU Result Parser</span>
          </div>

          {/* Heading */}
          <div className="auth-form-header">
            <h2 className="auth-form-title">Welcome</h2>
            <p className="auth-form-sub">
              Sign in with your Google account to access<br />your KTU result dashboard
            </p>
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

          {/* Google Sign-In button */}
          <button
            className={`auth-google-btn ${loading ? "auth-google-btn--loading" : ""}`}
            onClick={handleGoogle}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="auth-spinner" />
                Signing in…
              </>
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

          {/* Footer note */}
          <div className="auth-footer-note">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            Only your name and email are used. No data is stored externally.
          </div>

        </div>
      </div>

    </div>
  );
}

export default Auth;