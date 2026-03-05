import { useRef, useEffect } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import "./Features.css";

gsap.registerPlugin(ScrollTrigger);

/* ── SVG ILLUSTRATIONS ── */

const IllustrationParser = () => (
  <svg viewBox="0 0 400 280" className="feat-illustration" xmlns="http://www.w3.org/2000/svg">
    <g transform="translate(60, 40)">
      <animateTransform attributeName="transform" type="translate" values="60,40; 60,32; 60,40" dur="4s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1; 0.45 0 0.55 1"/>
      <rect x="0" y="0" width="110" height="145" rx="10" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.1)" strokeWidth="1"/>
      <rect x="0" y="0" width="110" height="32" rx="10" fill="rgba(239,68,68,0.15)"/>
      <rect x="0" y="22" width="110" height="10" fill="rgba(239,68,68,0.15)"/>
      <text x="12" y="22" fontSize="11" fontWeight="700" fill="rgba(239,68,68,0.9)" fontFamily="monospace">PDF</text>
      <rect x="12" y="42" width="86" height="5" rx="2" fill="rgba(255,255,255,0.15)"/>
      <rect x="12" y="53" width="70" height="5" rx="2" fill="rgba(255,255,255,0.1)"/>
      <rect x="12" y="64" width="80" height="5" rx="2" fill="rgba(255,255,255,0.1)"/>
      <rect x="12" y="75" width="60" height="5" rx="2" fill="rgba(255,255,255,0.08)"/>
      <rect x="12" y="90" width="86" height="44" rx="4" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" strokeWidth="1"/>
      <line x1="40" y1="90" x2="40" y2="134" stroke="rgba(255,255,255,0.08)" strokeWidth="1"/>
      <line x1="70" y1="90" x2="70" y2="134" stroke="rgba(255,255,255,0.08)" strokeWidth="1"/>
      <line x1="12" y1="104" x2="98" y2="104" stroke="rgba(255,255,255,0.08)" strokeWidth="1"/>
      <line x1="12" y1="118" x2="98" y2="118" stroke="rgba(255,255,255,0.08)" strokeWidth="1"/>
    </g>
    <g transform="translate(185, 115)">
      <line x1="0" y1="0" x2="40" y2="0" stroke="rgba(59,130,246,0.6)" strokeWidth="3" className="feat-dash"/>
      <polygon points="38,-5 50,0 38,5" fill="rgba(59,130,246,0.8)"/>
    </g>
    <g transform="translate(245, 40)">
      <animateTransform attributeName="transform" type="translate" values="240,40; 240,50; 240,40" dur="4s" begin="-1.5s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1; 0.45 0 0.55 1"/>
      <rect x="0" y="0" width="110" height="145" rx="10" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.1)" strokeWidth="1"/>
      <rect x="0" y="0" width="110" height="32" rx="10" fill="rgba(34,197,94,0.15)"/>
      <rect x="0" y="22" width="110" height="10" fill="rgba(34,197,94,0.15)"/>
      <text x="10" y="22" fontSize="10" fontWeight="700" fill="rgba(34,197,94,0.9)" fontFamily="monospace">XLSX</text>
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
      <rect x="12" y="134" width="35" height="5" rx="2" fill="rgba(34,197,94,0.4)"/>
      <rect x="52" y="134" width="22" height="5" rx="2" fill="rgba(34,197,94,0.25)"/>
      <rect x="79" y="134" width="28" height="5" rx="2" fill="rgba(34,197,94,0.35)"/>
    </g>
  </svg>
);

const IllustrationAccuracy = () => (
  <svg viewBox="0 0 360 260" className="feat-illustration" xmlns="http://www.w3.org/2000/svg">
    <g transform="translate(180, 130)">
      <circle cx="0" cy="0" r="90" fill="none" stroke="rgba(99,102,241,0.1)" strokeWidth="1.5"/>
      <circle cx="0" cy="0" r="70" fill="none" stroke="rgba(99,102,241,0.12)" strokeWidth="1.5"/>
      <circle cx="0" cy="0" r="50" fill="rgba(99,102,241,0.05)" stroke="rgba(99,102,241,0.2)" strokeWidth="1.5"/>
      <circle className="feat-spin-slow" cx="0" cy="0" r="90" fill="none" stroke="rgba(99,102,241,0.25)" strokeWidth="1.5" strokeDasharray="8 280" strokeLinecap="round"/>
      <text x="0" y="-8" textAnchor="middle" fontSize="26" fontWeight="800" fill="#ffffff" fontFamily="'Sora',sans-serif">100%</text>
      <text x="0" y="12" textAnchor="middle" fontSize="9" fontWeight="600" fill="rgba(255,255,255,0.4)" fontFamily="sans-serif" letterSpacing="2">ACCURACY</text>
      <circle cx="0" cy="30" r="10" fill="rgba(34,197,94,0.2)" stroke="rgba(34,197,94,0.5)" strokeWidth="1"/>
      <polyline points="-4,30 -1,33.5 5,26.5" fill="none" stroke="#34d399" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </g>
    <circle cx="270" cy="130" r="6" fill="#6366f1" style={{filter:'blur(0.5px)'}}/>
  </svg>
);

const IllustrationSpeed = () => (
  <svg viewBox="0 0 320 170" className="feat-illustration" xmlns="http://www.w3.org/2000/svg">
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
      <line x1="0" y1="0" x2="72" y2="-18" stroke="rgba(255,255,255,0.8)" strokeWidth="2" strokeLinecap="round"/>
      <circle cx="0" cy="0" r="6" fill="#ffffff"/>
      <circle cx="0" cy="0" r="3" fill="#3b82f6"/>
      <text x="-85" y="20" fontSize="9" fill="rgba(255,255,255,0.35)" fontFamily="sans-serif">0</text>
      <text x="75" y="20" fontSize="9" fill="rgba(255,255,255,0.35)" fontFamily="sans-serif">MAX</text>
      <text x="0" y="-25" textAnchor="middle" fontSize="18" fontWeight="800" fill="#ffffff" fontFamily="'Sora',sans-serif">0.8s</text>
      <text x="0" y="-10" textAnchor="middle" fontSize="8" fill="rgba(255,255,255,0.4)" fontFamily="sans-serif" letterSpacing="1">PER FILE</text>
    </g>
  </svg>
);

const IllustrationSecurity = () => (
  <svg viewBox="0 0 320 170" className="feat-illustration" xmlns="http://www.w3.org/2000/svg">
    <g transform="translate(160, 90)">
      <path d="M0,-65 L52,-40 L52,10 Q52,52 0,70 Q-52,52 -52,10 L-52,-40 Z"
        fill="rgba(245,158,11,0.06)" stroke="rgba(245,158,11,0.3)" strokeWidth="1.5"/>
      <rect x="-16" y="-5" width="32" height="26" rx="5" fill="rgba(245,158,11,0.15)" stroke="rgba(245,158,11,0.4)" strokeWidth="1.5"/>
      <path d="M -9 -5 L -9 -18 Q -9 -28 0 -28 Q 9 -28 9 -18 L 9 -5"
        fill="none" stroke="rgba(245,158,11,0.5)" strokeWidth="2" strokeLinecap="round"/>
      <circle cx="0" cy="8" r="4" fill="rgba(245,158,11,0.6)"/>
      <rect x="-2" y="10" width="4" height="6" rx="1" fill="rgba(245,158,11,0.6)"/>
    </g>
  </svg>
);

/* Internal Marks Merge illustration — shows two PDFs merging into one XLSX */
const IllustrationMerge = () => (
  <svg viewBox="0 0 320 170" className="feat-illustration" xmlns="http://www.w3.org/2000/svg">
    {/* Internal marks PDF */}
    <g transform="translate(18, 22)">
      <animateTransform attributeName="transform" type="translate" values="18,22; 18,14; 18,22" dur="4s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1; 0.45 0 0.55 1"/>
      <rect width="90" height="112" rx="8" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" strokeWidth="1"/>
      <rect x="0" y="0" width="90" height="24" rx="8" fill="rgba(239,68,68,0.14)"/>
      <rect x="0" y="16" width="90" height="8" fill="rgba(239,68,68,0.14)"/>
      <text x="9" y="16" fontSize="9" fontWeight="700" fill="rgba(239,68,68,0.8)" fontFamily="monospace">PDF</text>
      <text x="9" y="30" fontSize="7" fill="rgba(255,255,255,0.22)" fontFamily="sans-serif">Internal Marks</text>
      {[0,1,2,3].map(i => (
        <rect key={i} x="9" y={38 + i * 13} width={46 + (i%2)*16} height="5" rx="2" fill="rgba(255,255,255,0.07)"/>
      ))}
      <rect x="9" y="100" width="34" height="10" rx="3" fill="rgba(245,158,11,0.14)" stroke="rgba(245,158,11,0.28)" strokeWidth="0.5"/>
      <text x="13" y="108" fontSize="7" fontWeight="700" fill="rgba(245,158,11,0.75)" fontFamily="monospace">18/20</text>
    </g>

    {/* Result PDF */}
    <g transform="translate(18, 144)">
      <animateTransform attributeName="transform" type="translate" values="18,144; 18,152; 18,144" dur="5s" begin="-1.5s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1; 0.45 0 0.55 1"/>
      <rect width="90" height="18" rx="9" fill="rgba(59,130,246,0.1)" stroke="rgba(59,130,246,0.22)" strokeWidth="1"/>
      <text x="10" y="12.5" fontSize="8" fontWeight="600" fill="rgba(96,165,250,0.75)" fontFamily="sans-serif">Result PDF ↑</text>
    </g>

    {/* merge node */}
    <g transform="translate(160, 86)">
      <circle cx="0" cy="0" r="20" fill="rgba(99,102,241,0.1)" stroke="rgba(99,102,241,0.3)" strokeWidth="1.5"/>
      <circle className="feat-spin-slow" cx="0" cy="0" r="20" fill="none"
        stroke="rgba(99,102,241,0.18)" strokeWidth="1" strokeDasharray="4 28" strokeLinecap="round"/>
      <line x1="-7" y1="-5" x2="1" y2="0" stroke="#a5b4fc" strokeWidth="1.5" strokeLinecap="round"/>
      <line x1="-7" y1="5" x2="1" y2="0" stroke="#a5b4fc" strokeWidth="1.5" strokeLinecap="round"/>
      <line x1="1" y1="0" x2="10" y2="0" stroke="#a5b4fc" strokeWidth="1.5" strokeLinecap="round"/>
      <polygon points="9,-3 14,0 9,3" fill="#a5b4fc"/>
    </g>

    {/* connector lines */}
    <line x1="108" y1="78" x2="140" y2="84" stroke="rgba(99,102,241,0.28)" strokeWidth="1" strokeDasharray="3 3"/>
    <line x1="108" y1="94" x2="140" y2="88" stroke="rgba(59,130,246,0.28)" strokeWidth="1" strokeDasharray="3 3"/>

    {/* output XLSX */}
    <g transform="translate(196, 22)">
      <animateTransform attributeName="transform" type="translate" values="196,22; 196,14; 196,22" dur="3.5s" begin="-2s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1; 0.45 0 0.55 1"/>
      <rect width="96" height="112" rx="8" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" strokeWidth="1"/>
      <rect x="0" y="0" width="96" height="24" rx="8" fill="rgba(34,197,94,0.12)"/>
      <rect x="0" y="16" width="96" height="8" fill="rgba(34,197,94,0.12)"/>
      <text x="9" y="16" fontSize="9" fontWeight="700" fill="rgba(34,197,94,0.8)" fontFamily="monospace">XLSX</text>
      <text x="9" y="30" fontSize="7" fill="rgba(255,255,255,0.22)" fontFamily="sans-serif">Merged Output</text>
      {[0,1,2].map(col => (
        <rect key={col} x={9 + col * 25} y="36" width="21" height="8" rx="2"
          fill="rgba(34,197,94,0.14)" stroke="rgba(34,197,94,0.2)" strokeWidth="0.5"/>
      ))}
      {[0,1,2,3].map(row => [0,1,2].map(col => (
        <rect key={`${row}-${col}`}
          x={9 + col * 25} y={48 + row * 13}
          width="21" height="9" rx="2"
          fill={col === 2 ? "rgba(245,158,11,0.1)" : "rgba(255,255,255,0.04)"}
          stroke={col === 2 ? "rgba(245,158,11,0.18)" : "rgba(255,255,255,0.05)"}
          strokeWidth="0.5"/>
      )))}
      <text x="68" y="32" fontSize="6" fill="rgba(245,158,11,0.6)" fontFamily="sans-serif">int.</text>
    </g>

    {/* arrow from merge to output */}
    <line x1="180" y1="86" x2="194" y2="84" stroke="rgba(34,197,94,0.38)" strokeWidth="1.5" strokeDasharray="3 3"/>

    {/* bottom label */}
    <g transform="translate(198, 144)">
      <animateTransform attributeName="transform" type="translate" values="198,144; 198,136; 198,144" dur="4s" begin="-0.8s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1; 0.45 0 0.55 1"/>
      <rect width="92" height="18" rx="9" fill="rgba(245,158,11,0.09)" stroke="rgba(245,158,11,0.22)" strokeWidth="1"/>
      <text x="10" y="12.5" fontSize="7.5" fontWeight="600" fill="rgba(251,191,36,0.7)" fontFamily="sans-serif">+ internal marks col</text>
    </g>
  </svg>
);

/* ── CARD DATA — all features are real ── */
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
    id: "merge",
    layout: "short",
    color: "rose",
    tag: "Smart Merge",
    tagVariant: "rose",
    headline: <>Internal marks, <em>folded right in.</em></>,
    desc: "Attach your internal marks PDF alongside the result file. The pipeline merges both into one Excel sheet — external grades and internal scores, side by side.",
    quote: null,
    learnMore: false,
    visual: <IllustrationMerge />,
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
          <div className="feat-card-visual">{card.visual}</div>
          <div className="feat-card-body">
            <span className={`feat-tag feat-tag--${card.tagVariant}`}>{card.tag}</span>
            <h3 className="feat-headline">{card.headline}</h3>
            <p className="feat-desc">{card.desc}</p>
            {card.quote && <blockquote className="feat-quote">{card.quote}</blockquote>}
          </div>
        </>
      ) : (
        <>
          <div className="feat-card-visual">{card.visual}</div>
          <div className="feat-card-body">
            <span className={`feat-tag feat-tag--${card.tagVariant}`}>{card.tag}</span>
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

        <div className="features-header">
          <div className="features-eyebrow">
            <span className="features-eyebrow-dot" />
            MADE WITH ❤️ 
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