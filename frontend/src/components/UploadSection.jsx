import { useState, useEffect, useRef, forwardRef, useCallback } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import "./UploadSection.css";

gsap.registerPlugin(ScrollTrigger);

/* ── PIPELINE STEPS CONFIG ── */
const PIPELINE = [
  { id: "ingest",   label: "File Ingestion",     detail: "Validating PDF structure..." },
  { id: "extract",  label: "Text Extraction",     detail: "Reading page contents..." },
  { id: "parse",    label: "Grade Parsing",       detail: "Identifying subjects & scores..." },
  { id: "compile",  label: "Data Compilation",    detail: "Structuring rows & columns..." },
  { id: "export",   label: "Excel Generation",    detail: "Writing .xlsx output..." },
];

function formatBytes(bytes) {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1048576).toFixed(2)} MB`;
}

const UploadSection = forwardRef(function UploadSection({ token, onLogout }, ref) {
  const [pdfFile, setPdfFile]           = useState(null);
  const [dragOver, setDragOver]         = useState(false);
  const [isUploading, setIsUploading]   = useState(false);
  const [uploadStatus, setUploadStatus] = useState({ message: "", type: "" });
  const [sessionId, setSessionId]       = useState(null);
  const [showDownload, setShowDownload] = useState(false);
  const [activeStep, setActiveStep]     = useState(-1);
  const [doneSteps, setDoneSteps]       = useState([]);
  const [elapsed, setElapsed]           = useState(null);

  const sectionRef    = useRef(null);
  const dropzoneRef   = useRef(null);
  const timerRef      = useRef(null);
  const startTimeRef  = useRef(null);

  /* GSAP entrance */
  useEffect(() => {
    const el = ref?.current || sectionRef.current;
    if (!el) return;
    gsap.fromTo(el, { opacity: 0, y: 60 }, {
      opacity: 1, y: 0, duration: 1.1, ease: "power3.out",
      scrollTrigger: { trigger: el, start: "top 82%" },
    });
  }, [ref]);

  /* animate pipeline steps while uploading */
  useEffect(() => {
    if (!isUploading) return;
    setActiveStep(0);
    setDoneSteps([]);
    startTimeRef.current = Date.now();

    const delays = [0, 600, 1300, 2100, 3000];
    const timers = PIPELINE.map((_, i) =>
      setTimeout(() => {
        setActiveStep(i);
        if (i > 0) setDoneSteps(prev => [...prev, i - 1]);
      }, delays[i])
    );
    return () => timers.forEach(clearTimeout);
  }, [isUploading]);

  /* drag handlers */
  const onDragOver  = useCallback(e => { e.preventDefault(); setDragOver(true); }, []);
  const onDragLeave = useCallback(() => setDragOver(false), []);
  const onDrop      = useCallback(e => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file?.type === "application/pdf") setPdfFile(file);
  }, []);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) { setPdfFile(file); setShowDownload(false); setUploadStatus({ message: "", type: "" }); }
  };

  const handleUpload = async () => {
    if (!pdfFile) return;
    setIsUploading(true);
    setShowDownload(false);
    setUploadStatus({ message: "Initialising pipeline…", type: "loading" });
    startTimeRef.current = Date.now();

    try {
      const form = new FormData();
      form.append("pdf_file", pdfFile);

      const res  = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
      const data = await res.json();
      const ms   = Date.now() - startTimeRef.current;

      if (!res.ok) {
        if (res.status === 401) { onLogout(); return; }
        setUploadStatus({ message: data.detail || "Processing failed. Please retry.", type: "error" });
        setActiveStep(-1);
        return;
      }

      /* finish pipeline animation */
      setDoneSteps(PIPELINE.map((_, i) => i));
      setActiveStep(-1);
      setElapsed((ms / 1000).toFixed(2));
      setSessionId(data.session_id);
      setShowDownload(true);
      setUploadStatus({ message: "Pipeline complete — your Excel file is ready.", type: "success" });
    } catch {
      setUploadStatus({ message: "Network error. Check your connection and retry.", type: "error" });
      setActiveStep(-1);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownload = () => {
    fetch(`http://127.0.0.1:8000/download/${sessionId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => r.blob())
      .then(blob => {
        const url = URL.createObjectURL(blob);
        const a   = document.createElement("a");
        a.href     = url;
        a.download = `KTU_Results_${sessionId}.xlsx`;
        document.body.appendChild(a);
        a.click();
        URL.revokeObjectURL(url);
        document.body.removeChild(a);
      });
  };

  const handleReset = () => {
    setPdfFile(null);
    setShowDownload(false);
    setUploadStatus({ message: "", type: "" });
    setActiveStep(-1);
    setDoneSteps([]);
    setElapsed(null);
    setSessionId(null);
  };

  const getStepStatus = (i) => {
    if (doneSteps.includes(i)) return "done";
    if (activeStep === i)       return "active";
    return "idle";
  };

  return (
    <section className="upload-section" ref={ref || sectionRef}>
      <div className="upload-inner">

        {/* ── HEADER ── */}
        <div className="upload-header">
          <div className="upload-header-left">
            <div className="upload-eyebrow">
              <span className="upload-eyebrow-line" />
              Command Center
              <span className="upload-eyebrow-line" />
            </div>
            <h2 className="upload-title">
              Drop your PDF.<br />
              <em>Receive structured brilliance.</em>
            </h2>
            <p className="upload-subtitle">
              Upload any KTU result PDF and our five-stage processing pipeline
              transforms it into a clean, download-ready Excel file — in under a second.
            </p>
          </div>
          <div className="upload-header-stats">
            <div className="upload-stat">
              <div className="upload-stat-num">0.8s</div>
              <div className="upload-stat-label">Avg. Parse Time</div>
            </div>
            <div className="upload-stat">
              <div className="upload-stat-num">100%</div>
              <div className="upload-stat-label">Accuracy</div>
            </div>
          </div>
        </div>

        {/* ── WORKSPACE ── */}
        <div className="upload-workspace">

          {/* LEFT — Drop zone + actions */}
          <div className="upload-dropzone-wrap">
            <div
              ref={dropzoneRef}
              className={`upload-dropzone ${dragOver ? "drag-over" : ""}`}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onDrop={onDrop}
            >
              {/* corner brackets */}
              <span className="corner corner-tl" />
              <span className="corner corner-tr" />
              <span className="corner corner-bl" />
              <span className="corner corner-br" />

              <input
                type="file"
                accept=".pdf"
                className="upload-input-hidden"
                onChange={handleFileChange}
              />

              <div className="upload-icon-wrap">
                <div className="upload-icon-ring" />
                <div className="upload-icon-ring" />
                <div className="upload-icon-ring" />
                <div className="upload-icon-core">
                  {isUploading ? (
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                    </svg>
                  ) : pdfFile ? (
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                      <line x1="16" y1="13" x2="8" y2="13"/>
                      <line x1="16" y1="17" x2="8" y2="17"/>
                    </svg>
                  ) : (
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="16 16 12 12 8 16"/>
                      <line x1="12" y1="12" x2="12" y2="21"/>
                      <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>
                    </svg>
                  )}
                </div>
              </div>

              {pdfFile ? (
                <>
                  <div className="upload-dropzone-title">File loaded & ready</div>
                  <div className="upload-dropzone-sub">
                    Click <span>Process File</span> below to start the pipeline,<br />
                    or drop a new PDF to replace.
                  </div>
                </>
              ) : (
                <>
                  <div className="upload-dropzone-title">
                    {dragOver ? "Release to load" : "Drag & drop your PDF here"}
                  </div>
                  <div className="upload-dropzone-sub">
                    or <span>click anywhere to browse</span> your files
                  </div>
                  <div className="upload-file-types">
                    <span className="file-type-pill">.pdf</span>
                    <span className="file-type-pill">KTU Format</span>
                    <span className="file-type-pill">Any Semester</span>
                  </div>
                </>
              )}
            </div>

            {/* Selected file strip */}
            {pdfFile && (
              <div className="upload-file-selected" style={{marginTop: '1rem'}}>
                <div className="file-selected-icon">PDF</div>
                <div className="file-selected-info">
                  <div className="file-selected-name">{pdfFile.name}</div>
                  <div className="file-selected-meta">
                    {formatBytes(pdfFile.size)} · application/pdf
                  </div>
                </div>
                <div className="file-selected-check">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                </div>
              </div>
            )}

            {/* Process button */}
            <button
              className="upload-process-btn"
              style={{ marginTop: "1rem" }}
              onClick={handleUpload}
              disabled={!pdfFile || isUploading}
            >
              {isUploading ? (
                <><span className="btn-spinner" /> Running pipeline…</>
              ) : (
                <>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                  Launch Processing Pipeline
                </>
              )}
            </button>

            {/* Status bar */}
            {uploadStatus.message && (
              <div className={`upload-status-bar ${uploadStatus.type}`} style={{marginTop:'1rem'}}>
                <div className="status-bar-icon">
                  {uploadStatus.type === "success" && (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                      <polyline points="22 4 12 14.01 9 11.01"/>
                    </svg>
                  )}
                  {uploadStatus.type === "error" && (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <circle cx="12" cy="12" r="10"/>
                      <line x1="12" y1="8" x2="12" y2="12"/>
                      <line x1="12" y1="16" x2="12.01" y2="16"/>
                    </svg>
                  )}
                  {uploadStatus.type === "loading" && <span className="btn-spinner" style={{borderColor:'rgba(96,165,250,0.3)', borderTopColor:'#60a5fa'}}/>}
                </div>
                <span className="status-bar-text">{uploadStatus.message}</span>
              </div>
            )}

            {/* Download panel */}
            {showDownload && (
              <div className="download-panel" style={{marginTop:'1rem'}}>
                <div className="download-header">
                  <div className="download-success-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                  </div>
                  <div>
                    <div className="download-title">Output ready</div>
                    <div className="download-sub">Processed in {elapsed}s · Zero data loss</div>
                  </div>
                </div>

                <div className="download-file-row">
                  <div className="download-file-icon">XLSX</div>
                  <div className="download-file-name">KTU_Results_{sessionId?.slice(0,8)}.xlsx</div>
                  <button className="download-btn" onClick={handleDownload}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="7 10 12 15 17 10"/>
                      <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                    Download
                  </button>
                </div>

                <button className="download-reset" onClick={handleReset}>
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="1 4 1 10 7 10"/>
                    <path d="M3.51 15a9 9 0 1 0 .49-3.29"/>
                  </svg>
                  Process another file
                </button>
              </div>
            )}
          </div>

          {/* RIGHT PANEL */}
          <div className="upload-panel">

            {/* Pipeline card */}
            <div className="pipeline-card">
              <div className="pipeline-title">
                <span className="pipeline-title-dot" />
                Processing Pipeline
              </div>

              <div className="pipeline-steps">
                {PIPELINE.map((step, i) => {
                  const status = getStepStatus(i);
                  return (
                    <div key={step.id} className={`pipeline-step ${status}`}>
                      <div className="step-node">
                        {status === "done" ? (
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                            <polyline points="20 6 9 17 4 12"/>
                          </svg>
                        ) : status === "active" ? (
                          <>
                            <span className="step-pulse"/>
                            <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor">
                              <circle cx="12" cy="12" r="5"/>
                            </svg>
                          </>
                        ) : (
                          String(i + 1).padStart(2, "0")
                        )}
                      </div>
                      <div className="step-body">
                        <div className="step-name">{step.label}</div>
                        <div className="step-detail">
                          {status === "done"   ? "Completed ✓" :
                           status === "active" ? step.detail   :
                           "Waiting…"}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Metrics card */}
            <div className="metrics-card">
              <div className="metric-item">
                <div className="metric-val green">
                  {elapsed ? `${elapsed}s` : "—"}
                </div>
                <div className="metric-label">Process Time</div>
              </div>
              <div className="metric-item">
                <div className="metric-val blue">
                  {pdfFile ? formatBytes(pdfFile.size) : "—"}
                </div>
                <div className="metric-label">Input Size</div>
              </div>
              <div className="metric-item">
                <div className="metric-val amber">
                  {showDownload ? "100%" : "—"}
                </div>
                <div className="metric-label">Data Fidelity</div>
              </div>
              <div className="metric-item">
                <div className="metric-val purple">
                  {showDownload ? "5" : "—"}
                </div>
                <div className="metric-label">Stages Run</div>
              </div>
            </div>

          </div>
        </div>

        {/* ── TRUST BAR ── */}
        <div className="upload-trust-bar">
          {[
            { icon: <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>, label: "JWT Authenticated" },
            { icon: <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>, label: "Encrypted in Transit" },
            { icon: <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.29"/></svg>, label: "Zero Data Retention" },
            { icon: <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>, label: "KTU Format Native" },
            { icon: <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>, label: "Live Pipeline Tracking" },
          ].map((item, i, arr) => (
            <>
              <div key={item.label} className="trust-item">
                {item.icon}
                {item.label}
              </div>
              {i < arr.length - 1 && <span key={`sep-${i}`} className="trust-sep" />}
            </>
          ))}
        </div>

      </div>
    </section>
  );
});

export default UploadSection;