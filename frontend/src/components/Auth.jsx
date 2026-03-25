import { useState } from "react";
import "./Auth.css";
import { signInWithPopup, GoogleAuthProvider } from "firebase/auth";
import { auth } from "../firebase";
import logo from "../assets/ktulogo.png";

function Auth({ onAuthSuccess }) {
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  const handleGoogleLogin = async () => {
    setError("");
    setLoading(true);
    try {
      const provider = new GoogleAuthProvider();
      const result   = await signInWithPopup(auth, provider);
      onAuthSuccess(result.user);
    } catch (err) {
      console.error(err);
      if (err.code === "auth/popup-closed-by-user") {
        setError("Sign-in cancelled. Please try again.");
      } else if (err.code === "auth/network-request-failed") {
        setError("Network error. Check your connection.");
      } else {
        setError("Authentication failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="au">

      {/* ════════════════════════════════
          LEFT PANEL  — green brand side
          ════════════════════════════════ */}
      <div className="au__left">
        {/* dot-grid overlay */}
        <div className="au__left-grid" aria-hidden="true" />

        {/* decorative circles */}
        <div className="au__blob au__blob--1" aria-hidden="true" />
        <div className="au__blob au__blob--2" aria-hidden="true" />

        <div className="au__left-content">
      
          {/* College name */}
          <div className="au__left-brand">
            <h1 className="au__left-title">AISAT</h1>
            <p className="au__left-college">College of Engineering, Ernakulam</p>
            <div className="au__left-divider" />
            <p className="au__left-tagline">
              "Empowering faculty with intelligent result processing."
            </p>
          </div>

          {/* Feature pills */}
          <div className="au__left-pills">
            {["KTU PDF → Excel", "Internal Marks Merge", "Instant Download", "Zero Data Retention"].map(p => (
              <span key={p} className="au__left-pill">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                {p}
              </span>
            ))}
          </div>

        </div>
      </div>

      {/* ════════════════════════════════
          RIGHT PANEL — sign-in card
          ════════════════════════════════ */}
      <div className="au__right">
        <div className="au__card">

          {/* Card icon */}
          <div className="au__card-icon">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
          </div>

          {/* Heading */}
          <div className="au__card-head">
            <h2 className="au__card-title">Welcome back</h2>
            <p className="au__card-sub">
              Sign in with your Google account to start processing KTU result PDFs.
            </p>
          </div>

          {/* Google button */}
          <button
            className="au__btn-google"
            onClick={handleGoogleLogin}
            disabled={loading}
          >
            {loading ? (
              <span className="au__spinner" />
            ) : (
              <>
                <svg className="au__google-icon" viewBox="0 0 24 24" width="20" height="20">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Continue with Google
              </>
            )}
          </button>

          {/* Error */}
          {error && (
            <div className="au__error">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8"  x2="12"    y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              {error}
            </div>
          )}

          {/* Divider */}
          <div className="au__divider">
            <span className="au__divider-line" />
            <span className="au__divider-text">secured by</span>
            <span className="au__divider-line" />
          </div>

          {/* Trust grid */}
          <div className="au__trust-grid">
            {[
              {
                icon: <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>,
                label: "Firebase Auth",
                sub: "Google-secured login",
              },
              {
                icon: <><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></>,
                label: "AES-256",
                sub: "Encrypted in transit",
              },
              {
                icon: <><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.29"/></>,
                label: "Zero retention",
                sub: "Files deleted after use",
              },
              {
                icon: <><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></>,
                label: "Under 5s",
                sub: "Fast parse pipeline",
              },
            ].map(item => (
              <div key={item.label} className="au__trust-item">
                <div className="au__trust-icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                       stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    {item.icon}
                  </svg>
                </div>
                <p className="au__trust-label">{item.label}</p>
                <p className="au__trust-sub">{item.sub}</p>
              </div>
            ))}
          </div>

        </div>
      </div>

    </div>
  );
}

export default Auth;