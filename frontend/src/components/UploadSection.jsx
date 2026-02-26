import { useState, useEffect, forwardRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import "./UploadSection.css";

gsap.registerPlugin(ScrollTrigger);

const UploadSection = forwardRef(function UploadSection({ token, onLogout }, ref) {
  const [pdfFile, setPdfFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState({ message: "", type: "" });
  const [isUploading, setIsUploading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [showDownload, setShowDownload] = useState(false);

  useEffect(() => {
    if (ref?.current) {
      gsap.fromTo(
        ref.current,
        { opacity: 0, y: 50 },
        {
          opacity: 1,
          y: 0,
          duration: 1,
          ease: "power3.out",
          scrollTrigger: {
            trigger: ref.current,
            start: "top 80%",
          },
        }
      );
    }
  }, [ref]);

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
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        if (response.status === 401) {
          setUploadStatus({
            message: "Session expired. Please login again.",
            type: "error",
          });
          onLogout();
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
    } catch {
      setUploadStatus({
        message: "Network error. Please check your connection.",
        type: "error",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownload = () => {
    fetch(`http://127.0.0.1:8000/download/${sessionId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.blob())
      .then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `KTU_Results_${sessionId}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      });
  };

  return (
    <section className="upload-section" ref={ref}>
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
                <path
                  d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <polyline
                  points="14 2 14 8 20 8"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
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
                  <path
                    d="M13.3333 4L6 11.3333L2.66666 8"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <span>{pdfFile.name}</span>
              </div>
            )}
          </div>
        </div>

        <button
          className={`btn-process ${!pdfFile || isUploading ? "disabled" : ""}`}
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
                <path
                  d="M10 3.33334V16.6667M10 16.6667L15 11.6667M10 16.6667L5 11.6667"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </>
          )}
        </button>

        {showDownload && (
          <button className="btn-primary btn-download" onClick={handleDownload}>
            Download Excel
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path
                d="M10 3.33334V13.3333M10 13.3333L6.66667 10M10 13.3333L13.3333 10M3.33334 16.6667H16.6667"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        )}

        {uploadStatus.message && (
          <div className={`upload-status ${uploadStatus.type}`}>
            <div className="status-icon">
              {uploadStatus.type === "success" && (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M20 6L9 17L4 12"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              )}
              {uploadStatus.type === "error" && (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
                  <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
              )}
              {uploadStatus.type === "loading" && (
                <span className="spinner"></span>
              )}
            </div>
            <span>{uploadStatus.message}</span>
          </div>
        )}
      </div>
    </section>
  );
});

export default UploadSection;