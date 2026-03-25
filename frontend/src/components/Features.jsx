import { useEffect, useRef } from "react";
import "./Features.css";

/* ─── SVG Icons ──────────────────────────────────────────── */
const IconCheck = ({ size = 22 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
       stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
    <polyline points="22 4 12 14.01 9 11.01"/>
  </svg>
);
const IconShield = ({ size = 22 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
       stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
  </svg>
);
const IconMerge = ({ size = 22 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
       stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/>
    <path d="M6 9v6M18 15V9a6 6 0 0 0-6-6H9"/>
  </svg>
);
const IconGrid = ({ size = 22 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
       stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="7"/>
    <rect x="14" y="3" width="7" height="7"/>
    <rect x="14" y="14" width="7" height="7"/>
    <rect x="3" y="14" width="7" height="7"/>
  </svg>
);

/* ─── Excel row data ─────────────────────────────────────── */
const ROWS = [
  { roll: "AIK100", name: "Arun M.",   sgpa: "9.2", pass: true  },
  { roll: "AIK101", name: "Bhavya N.", sgpa: "8.9", pass: true  },
  { roll: "AIK102", name: "Edwin T.",  sgpa: "6.1", pass: false },
  { roll: "AIK103", name: "Devika S.", sgpa: "9.8", pass: true  },
];

const SEMESTERS = ["S1","S2","S3","S4","S5","S6","S7","S8"];

/* ════════════════════════════════════════════════════════════
   COMPONENT
   ════════════════════════════════════════════════════════════ */
export default function Features() {
  const ref = useRef(null);

  /* IntersectionObserver — add visible class card-by-card */
  useEffect(() => {
    const io = new IntersectionObserver(
      (entries) =>
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("ft__card--visible");
            io.unobserve(e.target);
          }
        }),
      { threshold: 0.1 }
    );
    ref.current?.querySelectorAll(".ft__card").forEach((c) => io.observe(c));
    return () => io.disconnect();
  }, []);

  return (
    <section className="ft" id="features" ref={ref}>

      {/* Ambient background decoration */}
      <div className="ft__ambient ft__ambient--tl" aria-hidden="true" />
      <div className="ft__ambient ft__ambient--br" aria-hidden="true" />

      <div className="ft__container">

        {/* ─── Section header ──────────────────────────────── */}
        <header className="ft__header">
          <span className="ft__eyebrow">Built for faculty</span>
          <h2 className="ft__headline">
            Every feature<br />has a reason.
          </h2>
          <p className="ft__sub">
            No bloat. No complexity you didn't ask for.<br />
            Just the tools you actually need.
          </p>
        </header>

        {/* ─── Bento grid ──────────────────────────────────── */}
        <div className="ft__bento">

          {/* ══ Card 1 — HERO: PDF → Excel (2 × 2) ══ */}
          <article className="ft__card ft__card--hero">
            <span className="ft__card-num">01</span>

            {/* Transformation visual */}
            <div className="ft__visual">

              {/* PDF mock */}
              <div className="ft__pdf">
                <div className="ft__pdf-bar">
                  <span className="ft__pdf-badge">PDF</span>
                  <span className="ft__pdf-filename">KTU_S5_Results.pdf</span>
                </div>
                <div className="ft__pdf-body">
                  {[75, 55, 85, 45, 65, 50].map((w, i) => (
                    <div key={i} className="ft__pdf-line" style={{ width: `${w}%` }} />
                  ))}
                </div>
              </div>

              {/* Animated flow arrow */}
              <div className="ft__flow">
                <div className="ft__flow-track">
                  <div className="ft__flow-dot ft__flow-dot--1" />
                  <div className="ft__flow-dot ft__flow-dot--2" />
                  <div className="ft__flow-dot ft__flow-dot--3" />
                </div>
                <svg className="ft__flow-chevron" width="18" height="18"
                     viewBox="0 0 24 24" fill="none" stroke="currentColor"
                     strokeWidth="2.5" strokeLinecap="round">
                  <line x1="5" y1="12" x2="19" y2="12"/>
                  <polyline points="12 5 19 12 12 19"/>
                </svg>
              </div>

              {/* Excel mock */}
              <div className="ft__excel">
                <div className="ft__excel-header">
                  {["Roll No", "Name", "SGPA", "Result"].map((h) => (
                    <div key={h} className="ft__excel-th">{h}</div>
                  ))}
                </div>
                {ROWS.map((row, i) => (
                  <div
                    key={row.roll}
                    className={`ft__excel-row${!row.pass ? " ft__excel-row--fail" : i % 2 ? " ft__excel-row--alt" : ""}`}
                    style={{ animationDelay: `${0.3 + i * 0.12}s` }}
                  >
                    <div className="ft__excel-td ft__excel-td--mono">{row.roll}</div>
                    <div className="ft__excel-td ft__excel-td--name">{row.name}</div>
                    <div className={`ft__excel-td ft__excel-td--num${!row.pass ? " ft__excel-td--num-fail" : ""}`}>
                      {row.sgpa}
                    </div>
                    <div className={`ft__excel-td ft__result--${row.pass ? "pass" : "fail"}`}>
                      {row.pass ? "PASS" : "FAIL"}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Text */}
            <div className="ft__card-body">
              <h3 className="ft__card-title">PDF becomes structured data.</h3>
              <p className="ft__card-desc">
                Upload any KTU result PDF. Every student, subject, grade, and credit
                is extracted and written into a perfectly structured Excel workbook.
                Zero copy-pasting.
              </p>
            </div>
          </article>

          {/* ══ Card 2 — SPEED (dark, 1 × 1) ══ */}
          <article className="ft__card ft__card--speed">
            <span className="ft__card-num ft__card-num--ghost">02</span>
            <div className="ft__speed-stat">
              <span className="ft__speed-num">0.8</span>
              <span className="ft__speed-unit">s</span>
            </div>
            <p className="ft__speed-tag">avg. parse time</p>
            <p className="ft__card-desc ft__card-desc--muted">
              Processed and ready to download before you can blink twice.
            </p>
            <div className="ft__speed-glow" aria-hidden="true" />
          </article>

          {/* ══ Card 3 — ACCURACY (1 × 1) ══ */}
          <article className="ft__card ft__card--accuracy">
            <span className="ft__card-num">03</span>
            <div className="ft__watermark" aria-hidden="true">100</div>
            <div className="ft__accuracy-body">
              <div className="ft__icon-box ft__icon-box--green">
                <IconCheck />
              </div>
              <h3 className="ft__card-title">100% grade accuracy.</h3>
              <p className="ft__card-desc">
                Validated against KTU's published schema on every parse.
              </p>
            </div>
          </article>

          {/* ══ Card 4 — SECURITY (1 × 1) ══ */}
          <article className="ft__card ft__card--security">
            <span className="ft__card-num">04</span>
            <div className="ft__icon-box ft__icon-box--green">
              <IconShield />
            </div>
            <h3 className="ft__card-title">Zero data retention.</h3>
            <p className="ft__card-desc">
              Files are processed in memory and discarded immediately.
              Nothing stored. Nothing shared.
            </p>
            <div className="ft__badge-row">
              <span className="ft__badge">Firebase Auth</span>
              <span className="ft__badge">AES-256</span>
            </div>
          </article>

          {/* ══ Card 5 — MERGE (1 × 1) ══ */}
          <article className="ft__card ft__card--merge">
            <span className="ft__card-num">05</span>
            <div className="ft__icon-box ft__icon-box--blue">
              <IconMerge />
            </div>
            <h3 className="ft__card-title">Internal marks, merged in.</h3>
            <p className="ft__card-desc">
              Upload a second PDF and the parser combines both workbooks — matching students by roll number automatically.
            </p>
            <div className="ft__merge-flow">
              <span className="ft__merge-pill ft__merge-pill--red">PDF</span>
              <span className="ft__merge-plus">+</span>
              <span className="ft__merge-pill ft__merge-pill--red">PDF</span>
              <span className="ft__merge-plus">→</span>
              <span className="ft__merge-pill ft__merge-pill--green">Excel</span>
            </div>
          </article>

          {/* ══ Card 6 — SEMESTERS (1 × 1) ══ */}
          <article className="ft__card ft__card--semesters">
            <span className="ft__card-num">06</span>
            <div className="ft__icon-box ft__icon-box--purple">
              <IconGrid />
            </div>
            <div className="ft__sem-grid">
              {SEMESTERS.map((s, i) => (
                <span
                  key={s}
                  className="ft__sem-pill"
                  style={{ animationDelay: `${i * 0.07}s` }}
                >
                  {s}
                </span>
              ))}
            </div>
            <h3 className="ft__card-title">Every semester.</h3>
            <p className="ft__card-desc">
              S1 through S8. All departments, any batch year. The parser adapts automatically.
            </p>
          </article>

        </div>
        {/* end bento */}

      </div>
    </section>
  );
}