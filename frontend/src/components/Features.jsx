import { useRef, useEffect } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import "./Features.css";

gsap.registerPlugin(ScrollTrigger);

/* ── SVG ILLUSTRATIONS ── */

const IllustrationParser = () => (
  <svg viewBox="0 0 400 280" className="feat-illustration" xmlns="http://www.w3.org/2000/svg">
    {/* PDF document */}
    <g className="feat-float" transform="translate(60, 40)">
      <rect x="0" y="0" width="110" height="145" rx="10" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.1)" strokeWidth="1"/>
      <rect x="0" y="0" width="110" height="32" rx="10" fill="rgba(239,68,68,0.15)"/>
      <rect x="0" y="22" width="110" height="10" fill="rgba(239,68,68,0.15)"/>
      <text x="12" y="22" fontSize="11" fontWeight="700" fill="rgba(239,68,68,0.9)" fontFamily="monospace">PDF</text>
      {/* text lines */}
      <rect x="12" y="42" width="86" height="5" rx="2" fill="rgba(255,255,255,0.15)"/>
      <rect x="12" y="53" width="70" height="5" rx="2" fill="rgba(255,255,255,0.1)"/>
      <rect x="12" y="64" width="80" height="5" rx="2" fill="rgba(255,255,255,0.1)"/>
      <rect x="12" y="75" width="60" height="5" rx="2" fill="rgba(255,255,255,0.08)"/>
      {/* table grid */}
      <rect x="12" y="90" width="86" height="44" rx="4" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" strokeWidth="1"/>
      <line x1="40" y1="90" x2="40" y2="134" stroke="rgba(255,255,255,0.08)" strokeWidth="1"/>
      <line x1="70" y1="90" x2="70" y2="134" stroke="rgba(255,255,255,0.08)" strokeWidth="1"/>
      <line x1="12" y1="104" x2="98" y2="104" stroke="rgba(255,255,255,0.08)" strokeWidth="1"/>
      <line x1="12" y1="118" x2="98" y2="118" stroke="rgba(255,255,255,0.08)" strokeWidth="1"/>
    </g>

    {/* scan / parse line */}
    <rect className="feat-scan-line" x="60" y="40" width="110" height="3" rx="1" fill="rgba(59,130,246,0.7)" style={{filter:'blur(1px)'}}/>

    {/* arrow */}
    <g transform="translate(190, 115)">
      <line x1="0" y1="0" x2="40" y2="0" stroke="rgba(59,130,246,0.6)" strokeWidth="2" className="feat-dash"/>
      <polygon points="38,-5 50,0 38,5" fill="rgba(59,130,246,0.8)"/>
    </g>

    {/* Excel output */}
    <g className="feat-float-2" transform="translate(245, 40)">
      <rect x="0" y="0" width="110" height="145" rx="10" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.1)" strokeWidth="1"/>
      <rect x="0" y="0" width="110" height="32" rx="10" fill="rgba(34,197,94,0.15)"/>
      <rect x="0" y="22" width="110" height="10" fill="rgba(34,197,94,0.15)"/>
      <text x="10" y="22" fontSize="10" fontWeight="700" fill="rgba(34,197,94,0.9)" fontFamily="monospace">XLSX</text>
      {/* spreadsheet cells */}
      {[0,1,2,3].map(row =>
        [0,1,2].map(col => (
          <rect key={`${row}-${col}`}
            x={12 + col * 28} y={42 + row * 22}
            width="24" height="16" rx="2"
            fill={row === 0 ? "rgba(34,197,94,0.12)" : "rgba(255,255,255,0.04)"}
            stroke="rgba(255,255,255,0.06)" strokeWidth="0.5"
          />
        ))
      )}
      {/* data bars */}
      <rect x="12" y="134" width="35" height="5" rx="2" fill="rgba(34,197,94,0.4)"/>
      <rect x="52" y="134" width="22" height="5" rx="2" fill="rgba(34,197,94,0.25)"/>
      <rect x="79" y="134" width="28" height="5" rx="2" fill="rgba(34,197,94,0.35)"/>
    </g>

    {/* floating badges */}
    <g className="feat-float-3" transform="translate(150, 195)">
      <rect x="0" y="0" width="100" height="28" rx="14" fill="rgba(59,130,246,0.15)" stroke="rgba(59,130,246,0.3)" strokeWidth="1"/>
      <circle cx="14" cy="14" r="5" fill="rgba(34,197,94,0.8)"/>
      <text x="24" y="18.5" fontSize="10" fontWeight="600" fill="rgba(255,255,255,0.7)" fontFamily="sans-serif">Parsed in 0.8s</text>
    </g>
  </svg>
);

const IllustrationAccuracy = () => (
  <svg viewBox="0 0 360 260" className="feat-illustration" xmlns="http://www.w3.org/2000/svg">
    {/* outer ring */}
    <g transform="translate(180, 130)">
      <circle cx="0" cy="0" r="90" fill="none" stroke="rgba(99,102,241,0.1)" strokeWidth="1.5"/>
      <circle cx="0" cy="0" r="70" fill="none" stroke="rgba(99,102,241,0.12)" strokeWidth="1.5"/>
      <circle cx="0" cy="0" r="50" fill="rgba(99,102,241,0.05)" stroke="rgba(99,102,241,0.2)" strokeWidth="1.5"/>
      {/* spinning orbit ring */}
      <circle className="feat-spin-slow" cx="0" cy="0" r="90" fill="none" stroke="rgba(99,102,241,0.25)" strokeWidth="1.5" strokeDasharray="8 280" strokeLinecap="round"/>
      {/* 100% text */}
      <text x="0" y="-8" textAnchor="middle" fontSize="26" fontWeight="800" fill="#ffffff" fontFamily="'Sora',sans-serif">100%</text>
      <text x="0" y="12" textAnchor="middle" fontSize="9" fontWeight="600" fill="rgba(255,255,255,0.4)" fontFamily="sans-serif" letterSpacing="2">ACCURACY</text>
      {/* checkmark */}
      <circle cx="0" cy="30" r="10" fill="rgba(34,197,94,0.2)" stroke="rgba(34,197,94,0.5)" strokeWidth="1"/>
      <polyline points="-4,30 -1,33.5 5,26.5" fill="none" stroke="#34d399" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </g>
    {/* orbit dot */}
    <circle cx="270" cy="130" r="6" fill="#6366f1" style={{filter:'blur(0.5px)'}}/>
    {/* floating data chips */}
    <g className="feat-float" transform="translate(20, 30)">
      <rect width="80" height="22" rx="11" fill="rgba(99,102,241,0.12)" stroke="rgba(99,102,241,0.25)" strokeWidth="1"/>
      <text x="12" y="15.5" fontSize="9" fontWeight="600" fill="rgba(255,255,255,0.5)" fontFamily="sans-serif">Grade: A+</text>
    </g>
    <g className="feat-float-2" transform="translate(260, 50)">
      <rect width="75" height="22" rx="11" fill="rgba(34,197,94,0.1)" stroke="rgba(34,197,94,0.25)" strokeWidth="1"/>
      <text x="10" y="15.5" fontSize="9" fontWeight="600" fill="rgba(52,211,153,0.7)" fontFamily="sans-serif">SGPA: 9.2</text>
    </g>
    <g className="feat-float-3" transform="translate(25, 200)">
      <rect width="90" height="22" rx="11" fill="rgba(245,158,11,0.1)" stroke="rgba(245,158,11,0.25)" strokeWidth="1"/>
      <text x="12" y="15.5" fontSize="9" fontWeight="600" fill="rgba(251,191,36,0.7)" fontFamily="sans-serif">Credits: 24</text>
    </g>
  </svg>
);

const IllustrationSpeed = () => (
  <svg viewBox="0 0 320 170" className="feat-illustration" xmlns="http://www.w3.org/2000/svg">
    {/* speedometer arc */}
    <g transform="translate(160, 110)">
      <path d="M -90 0 A 90 90 0 0 1 90 0" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="12" strokeLinecap="round"/>
      <path d="M -90 0 A 90 90 0 0 1 90 0" fill="none" stroke="url(#speedGrad)" strokeWidth="12" strokeLinecap="round"
        strokeDasharray="283" strokeDashoffset="40"/>
      <defs>
        <linearGradient id="speedGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#f59e0b"/>
          <stop offset="60%" stopColor="#3b82f6"/>
          <stop offset="100%" stopColor="#6366f1"/>
        </linearGradient>
      </defs>
      {/* needle */}
      <line x1="0" y1="0" x2="72" y2="-18" stroke="rgba(255,255,255,0.8)" strokeWidth="2" strokeLinecap="round"/>
      <circle cx="0" cy="0" r="6" fill="#ffffff"/>
      <circle cx="0" cy="0" r="3" fill="#3b82f6"/>
      {/* labels */}
      <text x="-85" y="20" fontSize="9" fill="rgba(255,255,255,0.35)" fontFamily="sans-serif">0</text>
      <text x="75" y="20" fontSize="9" fill="rgba(255,255,255,0.35)" fontFamily="sans-serif">MAX</text>
      <text x="0" y="-25" textAnchor="middle" fontSize="18" fontWeight="800" fill="#ffffff" fontFamily="'Sora',sans-serif">0.8s</text>
      <text x="0" y="-10" textAnchor="middle" fontSize="8" fill="rgba(255,255,255,0.4)" fontFamily="sans-serif" letterSpacing="1">PER FILE</text>
    </g>
    {/* ticks on arc */}
    {[0,30,60,90,120,150,180].map((deg, i) => {
      const angle = (deg - 90) * Math.PI / 180;
      const r1 = 80, r2 = 88;
      return (
        <line key={i}
          x1={160 + r1 * Math.cos(angle)} y1={110 + r1 * Math.sin(angle)}
          x2={160 + r2 * Math.cos(angle)} y2={110 + r2 * Math.sin(angle)}
          stroke="rgba(255,255,255,0.15)" strokeWidth="1.5"
        />
      );
    })}
  </svg>
);

const IllustrationSecurity = () => (
  <svg viewBox="0 0 320 170" className="feat-illustration" xmlns="http://www.w3.org/2000/svg">
    <g transform="translate(160, 90)">
      {/* shield */}
      <path d="M0,-65 L52,-40 L52,10 Q52,52 0,70 Q-52,52 -52,10 L-52,-40 Z"
        fill="rgba(245,158,11,0.06)" stroke="rgba(245,158,11,0.3)" strokeWidth="1.5"/>
      {/* lock body */}
      <rect x="-16" y="-5" width="32" height="26" rx="5" fill="rgba(245,158,11,0.15)" stroke="rgba(245,158,11,0.4)" strokeWidth="1.5"/>
      {/* lock shackle */}
      <path d="M -9 -5 L -9 -18 Q -9 -28 0 -28 Q 9 -28 9 -18 L 9 -5"
        fill="none" stroke="rgba(245,158,11,0.5)" strokeWidth="2" strokeLinecap="round"/>
      {/* keyhole */}
      <circle cx="0" cy="8" r="4" fill="rgba(245,158,11,0.6)"/>
      <rect x="-2" y="10" width="4" height="6" rx="1" fill="rgba(245,158,11,0.6)"/>
    </g>
    {/* orbiting security badges */}
    {[
      { angle: -40, label: 'JWT', color: '#f59e0b' },
      { angle: 50, label: 'HTTPS', color: '#34d399' },
      { angle: 150, label: 'AES', color: '#a5b4fc' },
    ].map(({ angle, label, color }, i) => {
      const rad = angle * Math.PI / 180;
      const r = 78;
      const x = 160 + r * Math.cos(rad);
      const y = 90 + r * Math.sin(rad);
      return (
        <g key={i} className={i % 2 === 0 ? 'feat-float' : 'feat-float-2'}>
          <rect x={x - 22} y={y - 11} width="44" height="22" rx="11"
            fill={`rgba(255,255,255,0.04)`} stroke={`${color}44`} strokeWidth="1"/>
          <text x={x} y={y + 4.5} textAnchor="middle" fontSize="9" fontWeight="700"
            fill={color} fontFamily="monospace">{label}</text>
        </g>
      );
    })}
  </svg>
);

const IllustrationBatch = () => (
  <svg viewBox="0 0 320 170" className="feat-illustration" xmlns="http://www.w3.org/2000/svg">
    {/* stacked file cards */}
    {[3,2,1,0].map(i => (
      <g key={i} transform={`translate(${80 + i*6}, ${35 + i*6})`} opacity={0.3 + i*0.18}>
        <rect width="90" height="115" rx="8"
          fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" strokeWidth="1"/>
      </g>
    ))}
    {/* front file */}
    <g transform="translate(80, 35)" className="feat-float">
      <rect width="90" height="115" rx="8" fill="rgba(255,255,255,0.05)" stroke="rgba(255,255,255,0.12)" strokeWidth="1"/>
      <rect x="0" y="0" width="90" height="26" rx="8" fill="rgba(239,68,68,0.18)"/>
      <rect x="0" y="18" width="90" height="8" fill="rgba(239,68,68,0.18)"/>
      <text x="10" y="18" fontSize="10" fontWeight="700" fill="rgba(239,68,68,0.9)" fontFamily="monospace">PDF</text>
      <rect x="10" y="35" width="70" height="4" rx="2" fill="rgba(255,255,255,0.1)"/>
      <rect x="10" y="45" width="55" height="4" rx="2" fill="rgba(255,255,255,0.07)"/>
      <rect x="10" y="55" width="65" height="4" rx="2" fill="rgba(255,255,255,0.07)"/>
    </g>
    {/* batch count badge */}
    <g className="feat-float-2" transform="translate(78, 128)">
      <rect width="96" height="22" rx="11" fill="rgba(59,130,246,0.15)" stroke="rgba(59,130,246,0.3)" strokeWidth="1"/>
      <text x="14" y="15.5" fontSize="9" fontWeight="600" fill="rgba(255,255,255,0.6)" fontFamily="sans-serif">+47 files queued</text>
    </g>
    {/* progress bar */}
    <rect x="200" y="70" width="95" height="8" rx="4" fill="rgba(255,255,255,0.05)"/>
    <rect x="200" y="70" width="95" height="8" rx="4" fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="1"/>
    <rect className="feat-progress-fill" x="200" y="70" width="95" height="8" rx="4" fill="url(#batchGrad)"/>
    <defs>
      <linearGradient id="batchGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stopColor="#3b82f6"/>
        <stop offset="100%" stopColor="#6366f1"/>
      </linearGradient>
    </defs>
    <text x="247" y="58" textAnchor="middle" fontSize="11" fontWeight="700" fill="rgba(255,255,255,0.6)" fontFamily="'Sora',sans-serif">Batch</text>
    <text x="247" y="100" textAnchor="middle" fontSize="9" fill="rgba(255,255,255,0.3)" fontFamily="sans-serif">Processing...</text>
    {/* mini check circles */}
    {[0,1,2].map(i => (
      <g key={i} transform={`translate(${205 + i*30}, 115)`}>
        <circle cx="0" cy="0" r="8" fill="rgba(34,197,94,0.15)" stroke="rgba(34,197,94,0.35)" strokeWidth="1"/>
        <polyline points="-3,0 -1,2.5 3.5,-2" fill="none" stroke="#34d399" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      </g>
    ))}
  </svg>
);

/* ── CARD DATA ── */
const cards = [
  {
    id: "parser",
    layout: "wide",
    color: "blue",
    tag: "Core Feature",
    tagVariant: "blue",
    headline: <>PDF-to-Excel? <em>Sheet</em> yeah.</>,
    desc: "Drop in your KTU result PDFs and watch the magic happen. Our parser reads every grade, credit, and SGPA line without breaking a sweat — delivering a perfectly structured Excel sheet, no manual copying required.",
    quote: <><strong>"What used to take our admin team 3 hours</strong> now finishes before we finish our morning chai."</>,
    learnMore: true,
    visual: <IllustrationParser />,
  },
  {
    id: "accuracy",
    layout: "tall",
    color: "indigo",
    tag: "Precision",
    tagVariant: "indigo",
    headline: <>Zero data left <em>behind.</em></>,
    desc: "Every grade, every subject code, every result status — captured with 100% fidelity. Our parser handles oddly formatted PDFs, multi-page results, and KTU's famously unpredictable layouts.",
    quote: <><strong>"Not a single SGPA</strong> was miscalculated in the making of this software."</>,
    learnMore: false,
    visual: <IllustrationAccuracy />,
  },
  {
    id: "speed",
    layout: "tall",
    color: "teal",
    tag: "Performance",
    tagVariant: "teal",
    headline: <>Faster than a <em>revaluation.</em></>,
    desc: "Process an entire semester's results in under a second. No waiting, no timeouts, no excuses — just instant structured data ready for download.",
    quote: null,
    learnMore: false,
    visual: <IllustrationSpeed />,
  },
  {
    id: "security",
    layout: "short",
    color: "amber",
    tag: "Security",
    tagVariant: "amber",
    headline: <>Your data doesn't <em>bunk class.</em></>,
    desc: "JWT auth, encrypted transit, and zero data retention. Your results stay yours — we never store your PDFs.",
    quote: null,
    learnMore: false,
    visual: <IllustrationSecurity />,
  },
  {
    id: "batch",
    layout: "short",
    color: "rose",
    tag: "Productivity",
    tagVariant: "rose",
    headline: <>Batch mode. <em>Because one PDF is never enough.</em></>,
    desc: "Queue up multiple result PDFs and let KTU Processor handle the whole semester in one go.",
    quote: null,
    learnMore: false,
    visual: <IllustrationBatch />,
  },
];

function Features() {
  const cardsRef = useRef([]);

  useEffect(() => {
    cardsRef.current.forEach((card, i) => {
      if (!card) return;
      gsap.fromTo(
        card,
        { opacity: 0, y: 40 },
        {
          opacity: 1,
          y: 0,
          duration: 0.9,
          delay: (i % 3) * 0.12,
          ease: "power3.out",
          scrollTrigger: {
            trigger: card,
            start: "top 88%",
          },
        }
      );
    });
  }, []);

  /* Render the 5 cards in Zoho's layout:
     Row 1: wide (full width)
     Row 2: tall + tall
     Row 3: short + short              */
  const wide   = cards.filter(c => c.layout === "wide");
  const talls  = cards.filter(c => c.layout === "tall");
  const shorts = cards.filter(c => c.layout === "short");

  const renderCard = (card, idx) => (
    <div
      key={card.id}
      ref={el => (cardsRef.current[idx] = el)}
      className={`feat-card feat-card--${card.layout} feat-card--${card.color}`}
    >
      {card.layout === "wide" ? (
        <>
          {/* wide: visual LEFT, text RIGHT */}
          <div className="feat-card-visual">{card.visual}</div>
          <div className="feat-card-body">
            <span className={`feat-tag feat-tag--${card.tagVariant}`}>
              {card.tag}
            </span>
            <h3 className="feat-headline">{card.headline}</h3>
            <p className="feat-desc">{card.desc}</p>
            {card.quote && <blockquote className="feat-quote">{card.quote}</blockquote>}
            {card.learnMore && (
              <button className="feat-learn-more">
                Learn more
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <line x1="5" y1="12" x2="19" y2="12"/>
                  <polyline points="12 5 19 12 12 19"/>
                </svg>
              </button>
            )}
          </div>
        </>
      ) : (
        <>
          <div className="feat-card-visual">{card.visual}</div>
          <div className="feat-card-body">
            <span className={`feat-tag feat-tag--${card.tagVariant}`}>
              {card.tag}
            </span>
            <h3 className="feat-headline">{card.headline}</h3>
            <p className="feat-desc">{card.desc}</p>
            {card.quote && <blockquote className="feat-quote">{card.quote}</blockquote>}
          </div>
        </>
      )}
    </div>
  );

  let idx = 0;

  return (
    <section className="features-section">
      <div className="features-inner">

        {/* Header */}
        <div className="features-header">
          <div className="features-eyebrow">
            <span className="features-eyebrow-dot" />
            Built Different
          </div>
          <h2 className="features-title">
            Everything your institution needs.<br />
            <em>Nothing it doesn't.</em>
          </h2>
          <p className="features-subtitle">
            KTU Processor is the only tool purpose-built for parsing Kerala Technological University
            result PDFs — with the accuracy and speed your admins deserve.
          </p>
        </div>

        {/* Card Grid */}
        <div className="features-grid">
          {wide.map(c  => renderCard(c, idx++))}
          {talls.map(c => renderCard(c, idx++))}
          {shorts.map(c => renderCard(c, idx++))}
        </div>

      </div>
    </section>
  );
}

export default Features;