import "./Hero.css";

function Hero({ onScrollToUpload }) {
  return (
    <section className="hero">
      {/* ── Background decorations ── */}
      <div className="hero__grid" aria-hidden="true" />
      <div className="hero__glow hero__glow--l" aria-hidden="true" />
      <div className="hero__glow hero__glow--r" aria-hidden="true" />

      <div className="hero__container">

        {/* Headline */}
        <h1 className="hero__headline">
          Turn KTU Result PDFs into
          <br />
          <span className="hero__headline-accent">Clean Excel Sheets</span>
          <br />
          in Seconds.
        </h1>

        <p className="hero__sub">
          Upload a KTU semester result PDF and instantly receive a structured,
          ready-to-use Excel workbook — with internal marks merged automatically.
          No manual copy-paste. No formatting headaches. Ever.
        </p>

        {/* CTA buttons */}
        <div className="hero__cta-row">
          <button className="hero__btn-primary" onClick={onScrollToUpload}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <polyline points="16 16 12 12 8 16"/>
              <line x1="12" y1="12" x2="12" y2="21"/>
              <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>
            </svg>
            Process Your Results
          </button>
        </div>


        {/* ═══════════ PRODUCT MOCKUP ═══════════ */}
        <div className="hero__mockup-wrap">
          <div className="hero__mockup">

            {/* Chrome bar */}
            <div className="hero__chrome">
              <div className="hero__chrome-dots">
                <span className="hero__dot" style={{ background: "#ff5f57" }} />
                <span className="hero__dot" style={{ background: "#febc2e" }} />
                <span className="hero__dot" style={{ background: "#28c840" }} />
              </div>
              <div className="hero__chrome-pill">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  <rect x="3" y="11" width="18" height="11" rx="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                aisat-ktu-parser.app
              </div>
              <div className="hero__chrome-r">
                <span /><span /><span />
              </div>
            </div>

            {/* Toolbar */}
            <div className="hero__toolbar">
              <div className="hero__tab hero__tab--active">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
                S5_CS_Results.xlsx
              </div>
              <div className="hero__tab">Summary</div>
              <div className="hero__toolbar-flex" />
              <div className="hero__dl-btn">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                Download
              </div>
            </div>

            {/* Spreadsheet */}
            <div className="hero__sheet">
              {/* Header row */}
              <div className="hero__row hero__row--head">
                <div className="hero__cell hero__cell--n">#</div>
                {["Roll No", "Name", "CST301", "CST303", "CST305", "MAT301", "HUT300", "SGPA", "Result"].map(h => (
                  <div key={h} className="hero__cell hero__cell--h">{h}</div>
                ))}
              </div>

              {/* Data */}
              {[
                { n:1, roll:"AIK20CS001", name:"Arun Mathew",    g:["A+","A", "B+","A", "A+"], sgpa:"9.2", pass:true  },
                { n:2, roll:"AIK20CS002", name:"Bhavya Nair",    g:["A", "A+","A", "B+","A" ], sgpa:"8.9", pass:true  },
                { n:3, roll:"AIK20CS003", name:"Christy Jose",   g:["B+","B", "A", "A", "B+"], sgpa:"8.4", pass:true  },
                { n:4, roll:"AIK20CS004", name:"Devika Suresh",  g:["A+","A+","A+","A+","A+"], sgpa:"9.8", pass:true  },
                { n:5, roll:"AIK20CS005", name:"Edwin Thomas",   g:["C", "B", "C+","B", "C" ], sgpa:"6.1", pass:false },
                { n:6, roll:"AIK20CS006", name:"Fathima Riyaz",  g:["A", "B+","A", "A", "A" ], sgpa:"8.7", pass:true  },
                { n:7, roll:"AIK20CS007", name:"George Philip",  g:["B", "B+","B", "B+","B" ], sgpa:"7.6", pass:true  },
              ].map(row => (
                <div key={row.n} className={`hero__row${!row.pass ? " hero__row--fail" : ""}`}>
                  <div className="hero__cell hero__cell--n">{row.n}</div>
                  <div className="hero__cell hero__cell--mono">{row.roll}</div>
                  <div className="hero__cell hero__cell--name">{row.name}</div>
                  {row.g.map((g,i) => (
                    <div key={i} className={`hero__cell hero__cell--grade hero__grade--${g.replace("+","p")}`}>{g}</div>
                  ))}
                  <div className="hero__cell hero__cell--sgpa">{row.sgpa}</div>
                  <div className={`hero__cell hero__cell--result ${row.pass ? "hero__result--pass" : "hero__result--fail"}`}>
                    {row.pass ? "PASS" : "FAIL"}
                  </div>
                </div>
              ))}

              {/* Status bar */}
              <div className="hero__statusbar">
                <span>7 students &nbsp;·&nbsp; Semester 5 &nbsp;·&nbsp; CSE</span>
                <div className="hero__statusbar-r">
                  <span className="hero__chip hero__chip--pass">6 Pass</span>
                  <span className="hero__chip hero__chip--fail">1 Fail</span>
                  <span>Avg SGPA: 8.39</span>
                </div>
              </div>
            </div>
          </div>
          {/* reflection */}
          <div className="hero__reflection" aria-hidden="true" />
        </div>

      </div>
    </section>
  );
}

export default Hero;