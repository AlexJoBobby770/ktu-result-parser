import { useState, useEffect, useRef, forwardRef, useCallback, Fragment } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import "./UploadSection.css";

gsap.registerPlugin(ScrollTrigger);

// ── Hardcoded for now — move to .env.local later ──────────────────────────
const API_URL = import.meta.env.VITE_API_URL;

function formatBytes(bytes) {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1048576).toFixed(2)} MB`;
}

const UploadSection = forwardRef(function UploadSection({ onLogout }, ref) {
  const [pdfFile, setPdfFile] = useState(null);
  const [batchYear, setBatchYear] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState({ message: "", type: "" });
  const [sessionId, setSessionId] = useState(null);
  const [showDownload, setShowDownload] = useState(false);
  const [elapsed, setElapsed] = useState(null);
  const [showExtraSheet, setShowExtraSheet] = useState(false);
  const [excelFile, setExcelFile] = useState(null);

  const sectionRef = useRef(null);
  const fileInputRef = useRef(null);
  const startTimeRef = useRef(null);

  /* GSAP entrance */
  useEffect(() => {
    const el = ref?.current || sectionRef.current;
    if (!el) return;
    gsap.fromTo(
      el.querySelectorAll(".us-animate"),
      { opacity: 0, y: 32 },
      {
        opacity: 1, y: 0,
        duration: 0.8,
        stagger: 0.1,
        ease: "power3.out",
        scrollTrigger: { trigger: el, start: "top 80%" },
      }
    );
  }, [ref]);

  /* drag handlers */
  const onDragOver = useCallback(e => { e.preventDefault(); setDragOver(true); }, []);
  const onDragLeave = useCallback(() => setDragOver(false), []);
  const onDrop = useCallback(e => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file?.type === "application/pdf") setPdfFile(file);
  }, []);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setPdfFile(file);
      setShowDownload(false);
      setUploadStatus({ message: "", type: "" });
    }
  };

  /* Sanitise batch year — digits only, max 4 chars */
  const handleBatchYearChange = (e) => {
    const val = e.target.value.replace(/\D/g, "").slice(0, 4);
    setBatchYear(val);
  };

  /*
    Normalise to 2-digit form before sending:
    "2022" → "22"   |   "22" → "22"   |   anything else → ""
  */
  const normalisedBatchYear = batchYear.length === 4
    ? batchYear.slice(2)
    : batchYear.length === 2
      ? batchYear
      : "";

  /* Both PDF and a valid 2-digit batch year are required */
  const canProcess = pdfFile !== null && normalisedBatchYear.length === 2;

  const handleUpload = async () => {
    if (!canProcess) return;
    setIsUploading(true);
    setShowDownload(false);
    setUploadStatus({ message: "Processing your file…", type: "loading" });
    startTimeRef.current = Date.now();

    try {
      const form = new FormData();
      form.append("pdf_file", pdfFile);
      form.append("batch_year", normalisedBatchYear);
      if (showExtraSheet && excelFile) form.append("internal_file", excelFile);

      // ── POST to /upload (not /download) ──────────────────────────────────
      const res = await fetch(`${API_URL}/upload`, { method: "POST", body: formData, });

      const data = await res.json();
      console.log("Upload response:", data);
      const ms = Date.now() - startTimeRef.current;

      if (!res.ok) {
        setUploadStatus({ message: data.detail || "Processing failed. Please retry.", type: "error" });
        return;
      }

      setElapsed((ms / 1000).toFixed(2));
      setSessionId(data.session_id);
      setShowDownload(true);
      setUploadStatus({ message: "Your Excel file is ready to download.", type: "success" });
    } catch (err) {
      console.error("Upload error:", err);
      setUploadStatus({ message: "Network error. Check your connection and retry.", type: "error" });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownload = () => {
    fetch(`${API_URL}/download/${sessionId}`)
      .then(r => r.blob())
      .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = Object.assign(document.createElement("a"), {
          href: url, download: `KTU_Results_${sessionId}.xlsx`
        });
        document.body.appendChild(a);
        a.click();
        URL.revokeObjectURL(url);
        document.body.removeChild(a);
      });
  };

  const handleReset = () => {
    setPdfFile(null);
    setBatchYear("");
    setShowDownload(false);
    setUploadStatus({ message: "", type: "" });
    setElapsed(null);
    setSessionId(null);
    setShowExtraSheet(false);
    setExcelFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleDownloadTemplate = () => {
    fetch(`${API_URL}/template`)
      .then(r => r.blob())
      .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = Object.assign(document.createElement("a"), {
          href: url, download: "KTU_Internal_Marks_Template.xlsx"
        });
        document.body.appendChild(a);
        a.click();
        URL.revokeObjectURL(url);
        document.body.removeChild(a);
      })
      .catch(err => console.error("Template download failed:", err));
  };

  return (
    <section className="us" ref={ref || sectionRef} id="upload">
      <div className="us__container">

        {/* ── Section label ── */}
        <div className="us__eyebrow us-animate">
          <span className="us__eyebrow-line" />
          Upload Your PDF
          <span className="us__eyebrow-line" />
        </div>

        {/* ── Headline ── */}
        <h2 className="us__headline us-animate">
          Drop your result PDF.<br />
          <span className="us__headline-accent">Get your Excel instantly.</span>
        </h2>
        <p className="us__sub us-animate">
          Our parser reads any KTU semester result PDF and converts it into a
          clean, structured Excel sheet — ready to share or archive in seconds.
        </p>

        {/* ══════════════════════ UPLOAD CARD ══════════════════════ */}
        <div className="us__card us-animate">

          {/* ── Drop zone ── */}
          <div
            className={`us__drop${dragOver ? " us__drop--over" : ""}${pdfFile ? " us__drop--loaded" : ""}`}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            onClick={() => !isUploading && fileInputRef.current?.click()}
            style={{ cursor: isUploading ? "default" : "pointer" }}
          >
            <input
              type="file"
              accept=".pdf"
              className="us__hidden-input"
              ref={fileInputRef}
              onChange={handleFileChange}
            />

            <span className="us__corner us__corner--tl" />
            <span className="us__corner us__corner--tr" />
            <span className="us__corner us__corner--bl" />
            <span className="us__corner us__corner--br" />

            <div className="us__drop-icon">
              {isUploading ? (
                <svg className="us__icon-spin" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
                </svg>
              ) : pdfFile ? (
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                </svg>
              ) : (
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                  <polyline points="16 16 12 12 8 16" />
                  <line x1="12" y1="12" x2="12" y2="21" />
                  <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" />
                </svg>
              )}
            </div>

            {pdfFile ? (
              <div className="us__drop-copy">
                <p className="us__drop-title">File ready</p>
                <p className="us__drop-hint">Drop a new PDF to replace, or press <strong>Process</strong> below</p>
              </div>
            ) : (
              <div className="us__drop-copy">
                <p className="us__drop-title">
                  {dragOver ? "Release to upload" : "Drag & drop your PDF here"}
                </p>
                <p className="us__drop-hint">
                  or <span className="us__drop-browse">click to browse</span> — KTU format, any semester
                </p>
                <div className="us__drop-pills">
                  <span className="us__pill">.pdf</span>
                  <span className="us__pill">KTU Format</span>
                  <span className="us__pill">Any Semester</span>
                </div>
              </div>
            )}
          </div>

          {/* ── Selected file row ── */}
          {pdfFile && (
            <div className="us__file-row">
              <div className="us__file-badge">PDF</div>
              <div className="us__file-info">
                <span className="us__file-name">{pdfFile.name}</span>
                <span className="us__file-meta">{formatBytes(pdfFile.size)} · application/pdf</span>
              </div>
              <button
                className="us__file-remove"
                onClick={handleReset}
                title="Remove file"
                aria-label="Remove file"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
          )}

          {/* ══ BATCH YEAR ROW ══ */}
          <div className="us__batch-row">
            <div className="us__batch-icon">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </div>

            <div className="us__batch-body">
              <label className="us__batch-label" htmlFor="batchYear">
                Batch year
                <span className="us__batch-required">required</span>
              </label>
              <p className="us__batch-sub">
                Enter the admission year (e.g. 2023). Only students from that batch will appear — seniors writing arrears are excluded automatically.
              </p>
            </div>

            <input
              id="batchYear"
              type="text"
              inputMode="numeric"
              className={`us__batch-input${normalisedBatchYear.length === 2 ? " us__batch-input--ok" : ""}`}
              placeholder="2022"
              value={batchYear}
              onChange={handleBatchYearChange}
              maxLength={4}
              disabled={isUploading}
            />
          </div>

          {/* Hint shown when PDF is selected but year isn't complete yet */}
          {pdfFile && normalisedBatchYear.length !== 2 && (
            <p className="us__batch-hint">
              ↑ Enter the 4-digit batch year to continue (e.g. <strong>2023</strong> for the 2023 intake)
            </p>
          )}
          <button
            type="button"
            className={`us__toggle${showExtraSheet ? " us__toggle--on" : ""}`}
            onClick={() => { setShowExtraSheet(v => !v); if (showExtraSheet) setExcelFile(null); }}
          >
            <div className="us__toggle-left">
              <div className="us__toggle-icon">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                  <rect x="3" y="3" width="18" height="18" rx="2" />
                  <path d="M3 9h18M9 21V9" />
                </svg>
              </div>
              <div>
                <p className="us__toggle-label">Attach internal marks PDF</p>
                <p className="us__toggle-sub">Optional · merges internal marks into output Excel</p>
              </div>
            </div>
            <div className="us__switch">
              <div className="us__switch-thumb" />
            </div>
          </button>

          {/* Internal marks file picker */}
          {showExtraSheet && (
            <label className="us__extra-drop">
              <input
                type="file"
                accept=".xlsx,.xls"
                style={{ display: "none" }}
                onChange={e => setExcelFile(e.target.files?.[0] || null)}
              />
              {excelFile ? (
                <div className="us__extra-file">
                  <div className="us__file-badge us__file-badge--sm">XLSX</div>
                  <div className="us__file-info">
                    <span className="us__file-name">{excelFile.name}</span>
                    <span className="us__file-meta">{formatBytes(excelFile.size)} · internal marks</span>
                  </div>
                  <div className="us__extra-check">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </div>
                </div>
              ) : (
                <div className="us__extra-empty">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                  <span>Click to browse <strong>internal marks PDF</strong></span>
                </div>
              )}
            </label>
          )}

          {/* ── Download Template button ── */}
          {showExtraSheet && (
            <button
              type="button"
              className="us__btn-template"
              onClick={(e) => { e.stopPropagation(); handleDownloadTemplate(); }}
              title="Download a pre-formatted Excel template for internal marks"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Download Excel Template
            </button>
          )}

          {/* ── Divider ── */}
          <div className="us__divider" />

          {/* ── Process button ── */}
          <button
            className="us__btn-process"
            onClick={handleUpload}
            disabled={!canProcess || isUploading}
          >
            {isUploading ? (
              <>
                <span className="us__spinner" />
                Processing…
              </>
            ) : (
              <>
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
                Process PDF
              </>
            )}
          </button>

          {/* ── Status message ── */}
          {uploadStatus.message && (
            <div className={`us__status us__status--${uploadStatus.type}`}>
              <span className="us__status-icon">
                {uploadStatus.type === "success" && (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" />
                  </svg>
                )}
                {uploadStatus.type === "error" && (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12.01" y2="16" />
                  </svg>
                )}
                {uploadStatus.type === "loading" && (
                  <span className="us__spinner us__spinner--blue" />
                )}
              </span>
              {uploadStatus.message}
            </div>
          )}

          {/* ── Download panel ── */}
          {showDownload && (
            <div className="us__download">
              <div className="us__download-left">
                <div className="us__download-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </div>
                <div>
                  <p className="us__download-title">Ready — processed in {elapsed}s</p>
                  <p className="us__download-file">KTU_Results_{sessionId?.slice(0, 8)}.xlsx</p>
                </div>
              </div>
              <div className="us__download-actions">
                <button className="us__btn-download" onClick={handleDownload}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                  </svg>
                  Download Excel
                </button>
                <button className="us__btn-reset" onClick={handleReset}>
                  Process another
                </button>
              </div>
            </div>
          )}

        </div>

        {/* ── Trust strip ── */}
        <div className="us__trust us-animate">
          {[
            {
              label: "Firebase authenticated",
              icon: <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            },
            {
              label: "Encrypted in transit",
              icon: <><rect x="3" y="11" width="18" height="11" rx="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" /></>
            },
            {
              label: "Zero data retention",
              icon: <><polyline points="1 4 1 10 7 10" /><path d="M3.51 15a9 9 0 1 0 .49-3.29" /></>
            },
            {
              label: "KTU native format",
              icon: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></>
            },
          ].map((item, i, arr) => (
            <Fragment key={item.label}>
              <div className="us__trust-item">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  {item.icon}
                </svg>
                {item.label}
              </div>
              {i < arr.length - 1 && <span className="us__trust-dot" />}
            </Fragment>
          ))}
        </div>

      </div>
    </section>
  );
});

export default UploadSection;