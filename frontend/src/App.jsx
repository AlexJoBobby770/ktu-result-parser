import "./App.css";
import { useEffect, useState } from "react";
import Footer from "./Footer";



function App() {
  const [backendStatus, setBackendStatus] = useState("checking");
  const [pdfFile, setPdfFile] = useState(null);
  const [masterFile, setMasterFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState({ message: "", type: "" });
  const [isUploading, setIsUploading] = useState(false);

  // Check backend connection on mount
  useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/health");
      if (response.ok) {
        const data = await response.json();
        setBackendStatus("connected");
      } else {
        throw new Error("Backend unavailable");
      }
    } catch (error) {
      setBackendStatus("disconnected");
      console.error("Backend connection error:", error);
    }
  };

  const handlePdfFileChange = (e) => {
    setPdfFile(e.target.files[0]);
    setUploadStatus({ message: "", type: "" });
  };

  const handleMasterFileChange = (e) => {
    setMasterFile(e.target.files[0]);
    setUploadStatus({ message: "", type: "" });
  };

  const handleUpload = async () => {
    // Validation
    if (!pdfFile || !masterFile) {
      setUploadStatus({
        message: "Please select both files",
        type: "error",
      });
      return;
    }

    if (!pdfFile.name.toLowerCase().endsWith(".pdf")) {
      setUploadStatus({
        message: "Please select a valid PDF file",
        type: "error",
      });
      return;
    }

    const masterExt = masterFile.name.toLowerCase();
    if (
      !masterExt.endsWith(".xlsx") &&
      !masterExt.endsWith(".xls") &&
      !masterExt.endsWith(".csv")
    ) {
      setUploadStatus({
        message: "Please select a valid Excel or CSV file",
        type: "error",
      });
      return;
    }

    // Upload
    setIsUploading(true);
    setUploadStatus({ message: "Uploading files...", type: "loading" });

    try {
      const formData = new FormData();
      formData.append("pdf_file", pdfFile);
      formData.append("master_file", masterFile);

      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setUploadStatus({
          message: result.message || "Files uploaded successfully!",
          type: "success",
        });
      } else {
        setUploadStatus({
          message: result.detail || "Upload failed. Please try again.",
          type: "error",
        });
      }
    } catch (error) {
      console.error("Upload error:", error);
      setUploadStatus({
        message: "Network error. Please check your connection.",
        type: "error",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    return (bytes / (1024 * 1024)).toFixed(2);
  };

  return (
    <> 
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <svg className="logo-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z" />
            </svg>
            <h1 className="header-title">KTU Result Processor</h1>
          </div>
          <div className="status-badge">
            {backendStatus === "connected" && (
              <>
                <span className="status-dot status-success"></span>
                <span className="status-text">Backend Online</span>
              </>
            )}
            {backendStatus === "disconnected" && (
              <>
                <span className="status-dot status-error"></span>
                <span className="status-text">Backend Offline</span>
              </>
            )}
            {backendStatus === "checking" && (
              <>
                <span className="status-dot status-checking"></span>
                <span className="status-text">Connecting...</span>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main">
        <div className="container">
          {/* Hero Section */}
          <section className="hero">
            <h2 className="hero-title">
              Process KTU Results with Ease
            </h2>
            <p className="hero-description">
              Upload your KTU result PDFs and student master files to generate
              structured Excel reports automatically.
            </p>
          </section>

          {/* Upload Card */}
          <section className="card">
            <div className="card-header">
              <h3 className="card-title">Upload Files</h3>
              <p className="card-description">
                Select both required files to begin processing
              </p>
            </div>

            <div className="card-body">
              {/* PDF File Upload */}
              <div className="file-upload-group">
                <label className="file-label">
                  <div className="label-header">
                    <span className="label-icon">📄</span>
                    <span className="label-text">KTU Result PDF</span>
                  </div>
                  <span className="label-requirement">Required • PDF only</span>
                </label>
                <div className="file-input-wrapper">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handlePdfFileChange}
                    className="file-input"
                    id="pdf-file"
                  />
                  <label htmlFor="pdf-file" className="file-input-button">
                    {pdfFile ? "Change file" : "Choose file"}
                  </label>
                  <div className={`file-display ${pdfFile ? "has-file" : ""}`}>
                    {pdfFile
                      ? `${pdfFile.name} (${formatFileSize(pdfFile.size)} MB)`
                      : "No file selected"}
                  </div>
                </div>
              </div>

              {/* Master File Upload */}
              <div className="file-upload-group">
                <label className="file-label">
                  <div className="label-header">
                    <span className="label-icon">📊</span>
                    <span className="label-text">Student Master File</span>
                  </div>
                  <span className="label-requirement">
                    Required • Excel or CSV
                  </span>
                </label>
                <div className="file-input-wrapper">
                  <input
                    type="file"
                    accept=".xlsx,.xls,.csv"
                    onChange={handleMasterFileChange}
                    className="file-input"
                    id="master-file"
                  />
                  <label htmlFor="master-file" className="file-input-button">
                    {masterFile ? "Change file" : "Choose file"}
                  </label>
                  <div
                    className={`file-display ${masterFile ? "has-file" : ""}`}
                  >
                    {masterFile
                      ? `${masterFile.name} (${formatFileSize(
                          masterFile.size
                        )} MB)`
                      : "No file selected"}
                  </div>
                </div>
              </div>

              {/* Upload Button */}
              <button
                onClick={handleUpload}
                disabled={!pdfFile || !masterFile || isUploading}
                className={`btn-primary ${
                  !pdfFile || !masterFile || isUploading ? "disabled" : ""
                }`}
              >
                {isUploading ? (
                  <>
                    <span className="spinner"></span>
                    Uploading...
                  </>
                ) : (
                  <>
                    <svg className="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                    Upload & Process
                  </>
                )}
              </button>

              {/* Status Message */}
              {uploadStatus.message && (
                <div className={`alert alert-${uploadStatus.type}`}>
                  {uploadStatus.type === "success" && (
                    <svg className="alert-icon" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                    </svg>
                  )}
                  {uploadStatus.type === "error" && (
                    <svg className="alert-icon" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
                    </svg>
                  )}
                  {uploadStatus.type === "loading" && (
                    <span className="spinner-small"></span>
                  )}
                  <span>{uploadStatus.message}</span>
                </div>
              )}
            </div>
          </section>

          {/* Features Section */}
          <section className="features">
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h4 className="feature-title">Fast Processing</h4>
              <p className="feature-description">
                Automatically parse and structure result data in seconds
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h4 className="feature-title">Analytics Ready</h4>
              <p className="feature-description">
                Generate performance reports and statistical insights
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h4 className="feature-title">Secure</h4>
              <p className="feature-description">
                Your data is processed securely and never stored
              </p>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
< Footer  />
    </div>
    </>
  );
}

export default App;