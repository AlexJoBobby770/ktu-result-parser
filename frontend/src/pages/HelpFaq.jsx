import { useState, useMemo } from "react";
import { Link } from "react-router-dom";
import "./HelpFaq.css";

const FAQS = [
  {
    category: "Getting Started",
    items: [
      {
        q: "What is KTU Processor?",
        a: "KTU Processor is a tool that converts KTU semester result PDFs into clean, structured Excel files. Upload your PDF, our 5-stage pipeline parses every subject, grade, and credit — then delivers a download-ready .xlsx file in under a second.",
      },
      {
        q: "What kind of PDFs does it support?",
        a: "It supports official KTU (APJ Abdul Kalam Technological University) semester result PDFs for any semester and any batch. Just make sure it's the original PDF from the KTU portal — scanned images won't work.",
      },
      {
        q: "Do I need to install anything?",
        a: "Nope. KTU Processor runs entirely in your browser. Just log in, upload your PDF, and download your Excel file. No installations required.",
      },
    ],
  },
  {
    category: "Uploading & Processing",
    items: [
      {
        q: "How do I upload my result PDF?",
        a: "Head to the Upload section on the home page. Either drag and drop your PDF onto the drop zone, or click anywhere inside it to browse your files. Once selected, hit 'Launch Processing Pipeline' and watch it go.",
      },
      {
        q: "What is the student details sheet?",
        a: "It's an optional Excel file (.xlsx or .csv) you can attach alongside your PDF. If provided, it enriches the output with student information like Name, Registration Number, and Branch. Expected columns are: Name, Reg No, Branch.",
      },
      {
        q: "How long does processing take?",
        a: "Usually under a second. Our average parse time is 0.8s. Larger PDFs with many pages may take up to 2–3 seconds.",
      },
      {
        q: "What if my PDF fails to process?",
        a: "Make sure the PDF is a genuine KTU result PDF (not a scan or image-based PDF). If it still fails, try re-downloading it from the KTU portal and uploading again. If the issue persists, reach out via the support links below.",
      },
    ],
  },
  {
    category: "Output & Download",
    items: [
      {
        q: "What does the output Excel file contain?",
        a: "The .xlsx output contains a structured table with all subjects, their subject codes, grades, credits, and SGPA/CGPA where available. If you attached a student details sheet, that info is merged in as well.",
      },
      {
        q: "Can I process multiple PDFs at once?",
        a: "Currently each upload processes one PDF at a time. After downloading your result, click 'Process another file' to start fresh with a new PDF.",
      },
      {
        q: "How long is my download available?",
        a: "Your output file is available to download immediately after processing. We don't retain any data after your session ends — so download before closing or refreshing the page.",
      },
    ],
  },
  {
    category: "Security & Privacy",
    items: [
      {
        q: "Is my data safe?",
        a: "Yes. All uploads are transmitted over HTTPS with AES-256 encryption. We use JWT-based authentication for every request. Most importantly — we have a zero data retention policy. Your files are processed in memory and never stored on our servers.",
      },
      {
        q: "Does KTU Processor store my result PDF?",
        a: "No. Your PDF is processed entirely in memory and discarded immediately after the Excel file is generated. We never write your files to disk or a database.",
      },
      {
        q: "Who can see my results?",
        a: "Only you. Each processing session is tied to your authenticated JWT token. No one else can access your session or download your output.",
      },
    ],
  },
];

function AccordionItem({ q, a }) {
  const [open, setOpen] = useState(false);
  return (
    <div className={`faq-item ${open ? "open" : ""}`}>
      <button className="faq-question" onClick={() => setOpen(v => !v)}>
        <span>{q}</span>
        <div className="faq-chevron">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
      </button>
      {open && (
        <div className="faq-answer">
          <p>{a}</p>
        </div>
      )}
    </div>
  );
}

export default function HelpFaq() {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    if (!query.trim()) return FAQS;
    const q = query.toLowerCase();
    return FAQS.map(cat => ({
      ...cat,
      items: cat.items.filter(
        item => item.q.toLowerCase().includes(q) || item.a.toLowerCase().includes(q)
      ),
    })).filter(cat => cat.items.length > 0);
  }, [query]);

  const totalResults = filtered.reduce((acc, cat) => acc + cat.items.length, 0);

  return (
    <div className="help-page">

      {/* ── HEADER ── */}
      <div className="help-header">
        <div className="help-header-inner">
          <Link to="/" className="help-back">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="19" y1="12" x2="5" y2="12"/>
              <polyline points="12 19 5 12 12 5"/>
            </svg>
            Back to Home
          </Link>

          <div className="help-eyebrow">
            <span className="help-eyebrow-line" />
            Help Center
            <span className="help-eyebrow-line" />
          </div>

          <h1 className="help-title">How can we <em>help you?</em></h1>
          <p className="help-subtitle">
            Everything you need to know about KTU Processor.
          </p>

          {/* Search */}
          <div className="help-search-wrap">
            <div className="help-search">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <input
                type="text"
                placeholder="Search questions…"
                value={query}
                onChange={e => setQuery(e.target.value)}
              />
              {query && (
                <button className="search-clear" onClick={() => setQuery("")}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              )}
            </div>
            {query && (
              <p className="search-result-count">
                {totalResults} result{totalResults !== 1 ? "s" : ""} for "<strong>{query}</strong>"
              </p>
            )}
          </div>
        </div>
      </div>

      {/* ── FAQ BODY ── */}
      <div className="help-body">
        <div className="help-body-inner">

          {filtered.length === 0 ? (
            <div className="help-empty">
              <div className="help-empty-icon">🔍</div>
              <div className="help-empty-title">No results found</div>
              <div className="help-empty-sub">Try a different search term or <button onClick={() => setQuery("")}>clear the search</button></div>
            </div>
          ) : (
            filtered.map(cat => (
              <div key={cat.category} className="faq-category">
                <div className="faq-category-header">
                  <span className="faq-category-icon">{cat.icon}</span>
                  <span className="faq-category-name">{cat.category}</span>
                  <span className="faq-category-count">{cat.items.length}</span>
                </div>
                <div className="faq-list">
                  {cat.items.map(item => (
                    <AccordionItem key={item.q} q={item.q} a={item.a} />
                  ))}
                </div>
              </div>
            ))
          )}

          {/* Contact strip */}
          <div className="help-contact">
            <div className="help-contact-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <div className="help-contact-body">
              <div className="help-contact-title">Still have questions?</div>
              <div className="help-contact-sub">Can't find what you're looking for? Reach out and we'll get back to you.</div>
            </div>
            <a href="https://mail.google.com/mail/?view=cm&to=harigovind.kr65@gmail.com" className="help-contact-btn">
              Contact Support
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/>
              </svg>
            </a>
          </div>

        </div>
      </div>
    </div>
  );
}