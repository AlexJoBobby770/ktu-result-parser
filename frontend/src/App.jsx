import "./App.css";
import { useEffect, useState, useRef } from "react";
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Auth from "./Auth";

gsap.registerPlugin(ScrollTrigger);

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [backendStatus, setBackendStatus] = useState("checking");
  const [pdfFile, setPdfFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState({ message: "", type: "" });
  const [isUploading, setIsUploading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [showDownload, setShowDownload] = useState(false);

  const heroRef = useRef(null);
  const uploadSectionRef = useRef(null);
  const featureCardsRef = useRef([]);

  useEffect(() => {
    // Check for existing token
    const savedToken = localStorage.getItem("token");
    if (savedToken) {
      setToken(savedToken);
      verifyToken(savedToken);
    }
    
    checkBackendConnection();
  }, []);

  useEffect(() => {
    if (!isAuthenticated) return;

    // Hero animation
    if (heroRef.current) {
      gsap.fromTo(
        heroRef.current.children,
        { opacity: 0, y: 30 },
        { 
          opacity: 1, 
          y: 0, 
          duration: 1,
          stagger: 0.2,
          ease: 'power3.out'
        }
      );
    }

    // Upload section animation
    if (uploadSectionRef.current) {
      gsap.fromTo(
        uploadSectionRef.current,
        { opacity: 0, y: 50 },
        {
          opacity: 1,
          y: 0,
          duration: 1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: uploadSectionRef.current,
            start: 'top 80%',
          }
        }
      );
    }

    // Feature cards animation
    featureCardsRef.current.forEach((card, index) => {
      if (card) {
        gsap.fromTo(
          card,
          { opacity: 0, y: 30 },
          {
            opacity: 1,
            y: 0,
            duration: 0.8,
            delay: index * 0.15,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: card,
              start: 'top 85%',
            }
          }
        );
      }
    });
  }, [isAuthenticated]);

  const verifyToken = async (authToken) => {
    try {
      const response = await fetch("http://127.0.0.1:8000/me", {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setCurrentUser(userData.username);
        setIsAuthenticated(true);
      } else {
        // Token invalid, clear it
        localStorage.removeItem("token");
        setToken(null);
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error("Token verification error:", error);
      localStorage.removeItem("token");
      setToken(null);
      setIsAuthenticated(false);
    }
  };

  const checkBackendConnection = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/health");
      if (response.ok) {
        setBackendStatus("connected");
      } else {
        throw new Error("Backend unavailable");
      }
    } catch (error) {
      setBackendStatus("disconnected");
      console.error("Backend connection error:", error);
    }
  };

  const handleAuthSuccess = (authToken) => {
    setToken(authToken);
    verifyToken(authToken);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setIsAuthenticated(false);
    setCurrentUser(null);
    setPdfFile(null);
    setUploadStatus({ message: "", type: "" });
    setShowDownload(false);
  };

  const handleUpload = async () => {
    if (!pdfFile) {
      setUploadStatus({ message: "Please select a PDF file", type: "error" });
      return;
    }

    setIsUploading(true);
    setUploadStatus({ message: "Processing your file...", type: "loading" });

    try {
      const formData = new FormData();
      formData.append("pdf_file", pdfFile);

      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const result = await response.json();
      
      if (!response.ok) {
        if (response.status === 401) {
          setUploadStatus({
            message: "Session expired. Please login again.",
            type: "error",
          });
          handleLogout();
          return;
        }
        
        setUploadStatus({
          message: result.detail || "Something went wrong. Please try again.",
          type: "error",
        });
        return;
      }

      setUploadStatus({
        message: "Success! Your file has been processed.",
        type: "success",
      });

      setSessionId(result.session_id);
      setShowDownload(true);

    } catch (error) {
      setUploadStatus({
        message: "Network error. Please check your connection.",
        type: "error",
      });
    } finally {
      setIsUploading(false);
    }
  };

  // Show auth screen if not authenticated
  if (!isAuthenticated) {
    return <Auth onAuthSuccess={handleAuthSuccess} />;
  }

  return (
    <div className="app">
      {/* Navigation */}
      <nav className="nav">
        <div className="nav-container">
          <div className="nav-logo">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <circle cx="16" cy="16" r="14" stroke="currentColor" strokeWidth="2"/>
              <path d="M12 16L15 19L20 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span>KTU Processor</span>
          </div>
          <div className="nav-status">
            <span className="nav-user">Hi, {currentUser}</span>
            <span className={`status-indicator ${backendStatus}`}></span>
            <span className="status-text">
              {backendStatus === "connected" && "Online"}
              {backendStatus === "disconnected" && "Offline"}
              {backendStatus === "checking" && "Connecting"}
            </span>
            <button className="btn-logout" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero" ref={heroRef}>
        <div className="hero-content">
          <h1 className="hero-title">
            Transform KTU Results<br/>Into Structured Data
          </h1>
          <p className="hero-subtitle">
            Automated processing for KTU result PDFs. Upload, process, and download 
            structured Excel reports in seconds.
          </p>
          <div className="hero-cta">
            <button className="btn-primary" onClick={() => uploadSectionRef.current?.scrollIntoView({ behavior: 'smooth' })}>
              Get Started
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M7 13L13 7M13 7H7M13 7V13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </section>

      {/* Upload Section */}
      <section className="upload-section" ref={uploadSectionRef}>
        <div className="section-header">
          <h2 className="section-title">Upload Your File</h2>
          <p className="section-description">
            Select your KTU student result PDF to begin processing
          </p>
        </div>

        <div className="upload-container">
          <div className="upload-grid-single">
            <div className="upload-card upload-card-single">
              <div className="upload-icon">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <polyline points="14 2 14 8 20 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="upload-title">Student Result PDF</h3>
              <p className="upload-description">KTU student result document</p>
              
              <label className="file-input-label">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setPdfFile(e.target.files[0])}
                  className="file-input-hidden"
                />
                <span className="file-input-button">
                  {pdfFile ? "Change File" : "Select PDF"}
                </span>
              </label>
              
              {pdfFile && (
                <div className="file-selected">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M13.3333 4L6 11.3333L2.66666 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  <span>{pdfFile.name}</span>
                </div>
              )}
            </div>
          </div>

          <button
            className={`btn-process ${(!pdfFile || isUploading) ? 'disabled' : ''}`}
            onClick={handleUpload}
            disabled={!pdfFile || isUploading}
          >
            {isUploading ? (
              <>
                <span className="spinner"></span>
                Processing...
              </>
            ) : (
              <>
                Process File
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M10 3.33334V16.6667M10 16.6667L15 11.6667M10 16.6667L5 11.6667" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </>
            )}
          </button>

          {showDownload && (
            <a 
              href={`http://127.0.0.1:8000/download/${sessionId}`}
              download
              className="btn-primary"
              onClick={(e) => {
                e.preventDefault();
                fetch(`http://127.0.0.1:8000/download/${sessionId}`, {
                  headers: {
                    Authorization: `Bearer ${token}`,
                  },
                })
                  .then(response => response.blob())
                  .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `KTU_Results_${sessionId}.xlsx`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                  });
              }}
            >
              Download Excel
            </a>
          )}

          {uploadStatus.message && (
            <div className={`upload-status ${uploadStatus.type}`}>
              <div className="status-icon">
                {uploadStatus.type === 'success' && (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                )}
                {uploadStatus.type === 'error' && (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                    <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                )}
                {uploadStatus.type === 'loading' && <span className="spinner"></span>}
              </div>
              <span>{uploadStatus.message}</span>
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-header">
          <h2 className="section-title">Why Choose Us</h2>
          <p className="section-description">
            Built for speed, accuracy, and simplicity
          </p>
        </div>

        <div className="features-grid">
          <div className="feature-card" ref={el => featureCardsRef.current[0] = el}>
            <div className="feature-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h3 className="feature-title">Lightning Fast</h3>
            <p className="feature-description">
              Process hundreds of records in seconds with our optimized parsing engine
            </p>
          </div>

          <div className="feature-card" ref={el => featureCardsRef.current[1] = el}>
            <div className="feature-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <line x1="12" y1="1" x2="12" y2="23" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h3 className="feature-title">100% Accurate</h3>
            <p className="feature-description">
              Advanced algorithms ensure zero data loss and perfect format conversion
            </p>
          </div>

          <div className="feature-card" ref={el => featureCardsRef.current[2] = el}>
            <div className="feature-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h3 className="feature-title">Secure</h3>
            <p className="feature-description">
              Your data is encrypted and protected with JWT authentication
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-left">
            <p>© 2024 KTU Processor. Built with FastAPI + React.</p>
          </div>
          <div className="footer-right">
            <span>Made by alex and ai alone</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;