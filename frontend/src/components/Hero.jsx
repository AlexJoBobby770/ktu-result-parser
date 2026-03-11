import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import "./Hero.css";

/* ── STARFIELD DATA ── */
const STARS = Array.from({ length: 80 }, (_, i) => ({
  id: i,
  top:    `${Math.random() * 100}%`,
  left:   `${Math.random() * 100}%`,
  size:   Math.random() * 2 + 0.5,
  dur:    `${Math.random() * 4 + 2}s`,
  delay:  `${Math.random() * 5}s`,
  minOp:  (Math.random() * 0.15 + 0.05).toFixed(2),
  maxOp:  (Math.random() * 0.5 + 0.3).toFixed(2),
}));

/* ── STREAM LOG LINES ── */
const STREAM_LINES = [
  { time: "00:00:01", module: "INGEST",  msg: "PDF structure validated — 4 pages detected",    ok: "OK" },
  { time: "00:00:02", module: "EXTRACT", msg: "Text layer extracted — 2,847 tokens",            ok: "OK" },
  { time: "00:00:03", module: "PARSE",   msg: "12 subjects identified across 4 semesters",      ok: "OK" },
  { time: "00:00:03", module: "COMPILE", msg: "Row schema built — 6 columns mapped",            ok: "OK" },
  { time: "00:00:04", module: "EXPORT",  msg: "XLSX generated — KTU_Results_a3f7.xlsx ready",   ok: "OK" },
  { time: "00:00:05", module: "SYSTEM",  msg: "Session closed — zero data retained",            ok: "OK" },
];

/* ── TICKER ITEMS (duplicated for infinite scroll) ── */
const TICKER = [
  {  label: "Avg Processing Time", val: "0.8s" },
  {  label: "Grade Accuracy",       val: "100%" },
  {  label: "Encryption",           val: "AES-256" },
  {  label: "Formats Supported",    val: "KTU PDF" },
  {  label: "Output Format",        val: "XLSX / Excel" },
  {  label: "Auth Protocol",        val: "Firebase" },
  {  label: "Data Retention",       val: "Zero" },
  {  label: "Pipeline Stages",      val: "5-Step" },
];

export default function Hero({ onScrollToUpload }) {
  const heroRef = useRef(null);

  useEffect(() => {
    const ctx = gsap.context(() => {

      /* ── SET initial positions FIRST, before timeline ── */
      gsap.set(".hero-chip",           { opacity: 0, y: 12 });
      gsap.set(".hero-headline",       { opacity: 1 });
      gsap.set(".hero-headline-inner", { y: "100%" });
      gsap.set(".hero-desc",           { opacity: 0, y: 16 });
      gsap.set(".hero-cta-row",        { opacity: 0, y: 16 });
      gsap.set(".hero-social-proof",   { opacity: 0, y: 16 });
      gsap.set(".hero-right",          { opacity: 0, x: 40 });
      gsap.set(".hero-ticker",         { opacity: 0 });

      /* ── THEN run timeline ── */
      const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

      tl.to(".hero-chip",           { opacity: 1, y: 0, duration: 0.7 }, 0.2)
        .to(".hero-headline-inner", { y: "0%", duration: 0.9, stagger: 0.12, ease: "power4.out" }, 0.55)
        .to(".hero-desc",           { opacity: 1, y: 0, duration: 0.7 }, 1.1)
        .to(".hero-cta-row",        { opacity: 1, y: 0, duration: 0.7 }, 1.3)
        .to(".hero-social-proof",   { opacity: 1, y: 0, duration: 0.7 }, 1.45)
        .to(".hero-right",          { opacity: 1, x: 0, duration: 1.0, ease: "power2.out" }, 0.7)
        .to(".hero-ticker",         { opacity: 1, duration: 0.6 }, 1.6);

    }, heroRef);

    return () => ctx.revert();
  }, []);

  /* re-animate cells on loop */
  useEffect(() => {
    const cells = document.querySelectorAll(".viz-cell");
    const cycleAnim = () => {
      cells.forEach((cell) => {
        gsap.fromTo(cell,
          { opacity: 0, scale: 0.7 },
          { opacity: 1, scale: 1, duration: 0.3,
            delay: parseFloat(cell.style.getPropertyValue("--cd") || "0") }
        );
      });
    };
    cycleAnim();
    const id = setInterval(cycleAnim, 5000);
    return () => clearInterval(id);
  }, []);

  return (
    <section className="hero" ref={heroRef}>

      {/* ── STARFIELD ── */}
      <div className="hero-starfield" aria-hidden>
        {STARS.map(s => (
          <span key={s.id} className="star" style={{
            top: s.top, left: s.left,
            width: s.size + "px", height: s.size + "px",
            "--dur":    s.dur,
            "--delay":  s.delay,
            "--min-op": s.minOp,
            "--max-op": s.maxOp,
          }} />
        ))}
      </div>

      {/* ── AURORA BLOBS ── */}
      <div className="hero-aurora" aria-hidden>
        <div className="aurora-1" />
        <div className="aurora-2" />
        <div className="aurora-3" />
      </div>

      {/* ── GRID ── */}
      <div className="hero-grid" aria-hidden />

      {/* ── MAIN CONTENT ── */}
      <div className="hero-content">

        {/* LEFT COLUMN */}
        <div className="hero-left">

          {/* Chip */}
          <div className="hero-chip">
            <span className="hero-chip-badge">
              <span className="chip-live-dot" />
              LIVE
            </span>
            KTU Result Parser · v2.0
          </div>

          {/* Headline */}
          <h1 className="hero-headline">
            <span className="hero-headline-line">
              <span className="hero-headline-inner">Your KTU results.</span>
            </span>
            <span className="hero-headline-line">
              <span className="hero-headline-inner">
                <em>Structured.</em>
              </span>
            </span>
            <span className="hero-headline-line">
              <span className="hero-headline-inner">
                In{" "}
                <span className="accent-word">under a second</span>
              </span>
            </span>
          </h1>

          {/* Description */}
          <p className="hero-desc">
            Tired of manually creating Excel sheet from result files? Our <strong>5-stage intelligent pipeline</strong> extracts,
            parses, and compiles every subject, grade, and credit into a{" "}
            <strong>clean Excel spreadsheet</strong> — ready to download and analyse.
          </p>

          {/* CTA row */}
          <div className="hero-cta-row">
            <button className="btn-hero-primary" onClick={onScrollToUpload}>
              Upload Your PDF
              <svg className="btn-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="7" y1="17" x2="17" y2="7" />
                <polyline points="7 7 17 7 17 17" />
              </svg>
            </button>
          </div>

          {/* Social proof */}
          <div className="hero-social-proof">
            <div className="proof-avatars">
              {["JD","DM","TV","NT"].map(initials => (
                <div key={initials} className="proof-avatar">{initials}</div>
              ))}
            </div>
            <div className="proof-text">
              <strong>6+ Faculties</strong> across Kerala<br />
              have already processed their results
            </div>
          </div>

        </div>

        {/* RIGHT COLUMN — Visualization */}
        <div className="hero-right">
          <div className="hero-viz">

            {/* Main card */}
            <div className="viz-card">

              {/* Top bar */}
              <div className="viz-topbar">
                <div className="viz-dots">
                  <span className="viz-dot"/><span className="viz-dot"/><span className="viz-dot"/>
                </div>
                <div className="viz-title-bar">pipeline.live</div>
                <div className="viz-status-pill">
                  <span className="chip-live-dot"/>
                  RUNNING
                </div>
              </div>

              {/* Transformation scene */}
              <div className="viz-scene">

                <div className="viz-transform-row">

                  {/* PDF input */}
                  <div className="viz-pdf-card">
                    <div className="viz-pdf-header">
                      <span className="viz-pdf-badge">PDF</span>
                      <span className="viz-pdf-name">kturesult.pdf</span>
                    </div>
                    <div className="viz-lines">
                      {[100, 85, 92, 70, 88, 60, 75, 95].map((w, i) => (
                        <div key={i} className="viz-line"
                          style={{ width: w + "%", "--d": `${i * 0.3}s` }} />
                      ))}
                    </div>
                  </div>

                  {/* Arrow */}
                  <div className="viz-arrow-col">
                    <div className="viz-arrow-track">
                      <div className="viz-arrow-ring"/>
                      <div className="viz-arrow-ring"/>
                      <div className="viz-arrow-icon">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                          <line x1="5" y1="12" x2="19" y2="12"/>
                          <polyline points="12 5 19 12 12 19"/>
                        </svg>
                      </div>
                    </div>
                    <div className="viz-arrow-label">5 stages</div>
                  </div>

                  {/* XLSX output */}
                  <div className="viz-xlsx-card">
                    <div className="viz-xlsx-header">
                      <span className="viz-xlsx-badge">XLSX</span>
                      <span className="viz-pdf-name">results.xlsx</span>
                    </div>
                    <div className="viz-cells">
                      {Array.from({ length: 18 }, (_, i) => (
                        <div key={i} className={`viz-cell ${i < 3 ? "header-cell" : ""}`}
                          style={{ "--cd": `${i * 0.08}s` }} />
                      ))}
                    </div>
                  </div>

                </div>

                {/* Log stream */}
                <div className="viz-stream">
                  {[...STREAM_LINES, ...STREAM_LINES].map((line, i) => (
                    <div key={i} className="stream-row" style={{ "--sr": `${(i % STREAM_LINES.length) * 1.3}s` }}>
                      <span className="stream-time">{line.time}</span>
                      <span className="stream-module">[{line.module}]</span>
                      <span className="stream-msg">{line.msg}</span>
                      <span className="stream-ok">{line.ok}</span>
                    </div>
                  ))}
                </div>

              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── TICKER ── */}
      <div className="hero-ticker">
        <div className="ticker-track">
          {[...TICKER, ...TICKER].map((item, i) => (
            <span key={i} className="ticker-item">
              <span>{item.label}</span>
              <span className="ticker-val">{item.val}</span>
              <span className="ticker-sep">·</span>
            </span>
          ))}
        </div>
      </div>

    </section>
  );
}