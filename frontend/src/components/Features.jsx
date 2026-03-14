import "./Features.css";

/* ── Icon components ──────────────────────────────────────── */
const IconPDF = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
    <line x1="16" y1="13" x2="8" y2="13"/>
    <line x1="16" y1="17" x2="8" y2="17"/>
  </svg>
);
const IconSheet = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="18" height="18" rx="2"/>
    <path d="M3 9h18M3 15h18M9 3v18"/>
  </svg>
);
const IconMerge = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/>
    <path d="M6 9v6M18 15V9a6 6 0 0 0-6-6H9"/>
  </svg>
);
const IconLock = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
  </svg>
);
const IconSpeed = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
  </svg>
);
const IconCheck = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
    <polyline points="22 4 12 14.01 9 11.01"/>
  </svg>
);

/* ── Small checkmark for bullet lists ────────────────────── */
const Tick = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

/* ════════════════════════════════════════════════════════════
   FEATURE CARDS DATA
   ════════════════════════════════════════════════════════════ */
const CARDS = [
  {
    icon: <IconPDF />,
    color: "red",
    title: "Reads any KTU PDF",
    text: "Handles all semesters and departments. No reformatting or pre-processing needed — just upload and go.",
  },
  {
    icon: <IconSheet />,
    color: "green",
    title: "Structured Excel output",
    text: "Every student, subject, and grade lands in the right column. Clean headers, consistent formatting, ready to share.",
  },
  {
    icon: <IconMerge />,
    color: "blue",
    title: "Internal marks merge",
    text: "Upload a second PDF of internal marks and the parser combines both into a single unified workbook automatically.",
  },
  {
    icon: <IconLock />,
    color: "amber",
    title: "Zero data retention",
    text: "Files are processed in-memory and discarded immediately. Nothing is stored, logged, or shared after your download.",
  },
  {
    icon: <IconSpeed />,
    color: "purple",
    title: "Under 5 seconds",
    text: "The entire parse-to-download pipeline runs in seconds — not minutes. Fast enough for live use in the exam office.",
  },
  {
    icon: <IconCheck />,
    color: "teal",
    title: "100% grade accuracy",
    text: "Grades, SGPA, and result status are validated against KTU's published schema so nothing slips through.",
  },
];

/* ════════════════════════════════════════════════════════════
   COMPONENT
   ════════════════════════════════════════════════════════════ */
function Features() {
  return (
    <section className="ft" id="features">
      <div className="ft__container">

        {/* ── Section header ── */}
        <div className="ft__header">
          <p className="ft__eyebrow">Why faculty love it</p>
          <h2 className="ft__headline">
            Everything you need.<br />
            <span className="ft__headline-accent">Nothing you don't.</span>
          </h2>
          <p className="ft__sub">
            Built specifically for AISAT faculty — every feature maps to a real
            pain point in the KTU result workflow.
          </p>
        </div>

        {/* ── 3-column feature grid ── */}
        <div className="ft__grid">
          {CARDS.map((card) => (
            <div key={card.title} className="ft__card">
              <div className={`ft__card-icon ft__card-icon--${card.color}`}>
                {card.icon}
              </div>
              <h3 className="ft__card-title">{card.title}</h3>
              <p className="ft__card-text">{card.text}</p>
            </div>
          ))}
        </div>

        {/* ── Large two-column highlight ── */}
        <div className="ft__highlight">

          {/* Left: visual mock of merged output */}
          <div className="ft__hl-visual">
            <div className="ft__hl-visual-label">Output preview</div>

            {/* Mini spreadsheet */}
            <div className="ft__mini-sheet">
              <div className="ft__mini-row ft__mini-row--head">
                {["Roll No", "Name", "Int.", "Ext.", "Total", "Grade"].map(h => (
                  <div key={h} className="ft__mini-cell ft__mini-cell--h">{h}</div>
                ))}
              </div>
              {[
                { roll: "CS001", name: "Arun M.", int: 23, ext: 61, total: 84, grade: "A+", pass: true  },
                { roll: "CS002", name: "Bhavya N.", int: 21, ext: 57, total: 78, grade: "A",  pass: true  },
                { roll: "CS003", name: "Christy J.", int: 19, ext: 52, total: 71, grade: "B+", pass: true  },
                { roll: "CS004", name: "Devika S.", int: 24, ext: 65, total: 89, grade: "A+", pass: true  },
                { roll: "CS005", name: "Edwin T.", int: 14, ext: 38, total: 52, grade: "C",  pass: false },
              ].map(row => (
                <div key={row.roll} className={`ft__mini-row${!row.pass ? " ft__mini-row--fail" : ""}`}>
                  <div className="ft__mini-cell ft__mini-cell--mono">{row.roll}</div>
                  <div className="ft__mini-cell ft__mini-cell--name">{row.name}</div>
                  <div className="ft__mini-cell ft__mini-cell--int">{row.int}</div>
                  <div className="ft__mini-cell ft__mini-cell--ext">{row.ext}</div>
                  <div className="ft__mini-cell ft__mini-cell--total">{row.total}</div>
                  <div className={`ft__mini-cell ft__mini-cell--grade ft__grade--${row.grade.replace("+","p")}`}>{row.grade}</div>
                </div>
              ))}
              <div className="ft__mini-status">
                <span>5 students · CS301 · Merged output</span>
                <span className="ft__mini-chip ft__mini-chip--green">Internal ✓</span>
              </div>
            </div>

            {/* Floating merge badge */}
            <div className="ft__merge-badge">
              <div className="ft__merge-badge-icon">
                <IconMerge />
              </div>
              <div>
                <p className="ft__merge-badge-title">Auto-merged</p>
                <p className="ft__merge-badge-sub">Internal + External</p>
              </div>
            </div>
          </div>

          {/* Right: text content */}
          <div className="ft__hl-body">
            <p className="ft__hl-eyebrow">Highlight feature</p>
            <h3 className="ft__hl-title">
              Internal marks,<br />merged automatically.
            </h3>
            <p className="ft__hl-text">
              Manually combining internal marks with published KTU results used
              to mean hours of copy-pasting. Now it takes one extra file upload.
              The parser matches students by roll number and adds an internal
              marks column — no spreadsheet formulas required.
            </p>
            <ul className="ft__hl-list">
              {[
                "Matches by roll number — no manual alignment",
                "Calculates total marks automatically",
                "Flags mismatches so nothing is silently wrong",
                "Works even if row order differs between PDFs",
              ].map(item => (
                <li key={item} className="ft__hl-item">
                  <span className="ft__hl-tick"><Tick /></span>
                  {item}
                </li>
              ))}
            </ul>
          </div>

        </div>
        {/* end highlight */}

      </div>
    </section>
  );
}

export default Features;