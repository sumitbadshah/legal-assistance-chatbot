import React, { useState, useEffect, useRef } from "react";
import { Scale, MessageSquare, FileText, ClipboardCheck, Landmark, Send, Sun, Moon, Download, ThumbsUp, ThumbsDown, Loader2, Stamp, Mic, MicOff, Settings, LogOut, Server, X } from "lucide-react";



const LANGUAGES = ["English", "Hindi", "Marathi", "Gujarati", "Tamil", "Telugu", "Kannada", "Bengali"];

const SPEECH_LOCALE = {
  English: "en-IN", Hindi: "hi-IN", Marathi: "mr-IN", Gujarati: "gu-IN",
  Tamil: "ta-IN", Telugu: "te-IN", Kannada: "kn-IN", Bengali: "bn-IN",
};

const DOC_TYPES = {
  affidavit: { label: "Affidavit", fields: ["Deponent name", "Father's/Husband's name", "Address", "Purpose of affidavit", "Statement of facts"] },
  rental: { label: "Rental Agreement", fields: ["Landlord name", "Tenant name", "Property address", "Monthly rent", "Duration (months)", "Start date"] },
  notice: { label: "Legal Notice", fields: ["Sender name", "Recipient name", "Subject", "Facts / grievance", "Relief demanded"] },
  nda: { label: "Non-Disclosure Agreement", fields: ["Party A", "Party B", "Purpose of disclosure", "Effective date", "Duration (months)"] },
  will: { label: "Will", fields: ["Testator name", "Address", "Beneficiaries", "Executor name", "Assets to bequeath"] },
  custom: { label: "Other (describe)", fields: ["Type of document", "Details / requirements"] },
};

const GOV_SERVICES = [
  {
    name: "Aadhaar", desc: "Enrol, update, or download your 12-digit biometric ID.", portal: "uidai.gov.in",
    legalBasis: "Aadhaar Act, 2016", fee: "Free for new enrolment; ₹50 for updates/corrections", timeline: "90 days for card delivery after enrolment",
    documents: ["Proof of Identity (Passport/PAN/Voter ID)", "Proof of Address (utility bill/bank statement)", "Proof of Date of Birth (birth certificate/10th marksheet)"],
    steps: [
      "Locate your nearest Aadhaar Enrolment Centre via uidai.gov.in or book a slot online.",
      "Carry original identity, address, and date-of-birth documents.",
      "Complete demographic details and biometric capture (fingerprints, iris scan, photo) at the centre.",
      "Collect your Enrolment ID (EID) slip — used to track status.",
      "Download the e-Aadhaar or receive the physical card by post within about 90 days.",
    ],
  },
  {
    name: "PAN Card", desc: "Apply for or correct your Permanent Account Number for tax purposes.", portal: "incometax.gov.in / NSDL / UTIITSL",
    legalBasis: "Income-tax Act, 1961, Section 139A", fee: "₹107 (physical card, Indian address) / ₹1,017 (foreign address)", timeline: "15–20 working days",
    documents: ["Proof of Identity (Aadhaar/Passport/Voter ID)", "Proof of Address", "Proof of Date of Birth", "Passport-size photograph"],
    steps: [
      "Fill Form 49A (Indian citizens) online at the NSDL or UTIITSL portal.",
      "Upload scanned photo, signature, and supporting documents.",
      "Pay the applicable fee online.",
      "e-Sign or e-KYC using Aadhaar-linked OTP, or courier a physical acknowledgment with documents.",
      "Track status using the 15-digit acknowledgment number; receive PAN by post/email.",
    ],
  },
  {
    name: "Passport", desc: "Apply for a fresh passport, renewal, or police-verification tracking.", portal: "passportindia.gov.in",
    legalBasis: "Passports Act, 1967", fee: "₹1,500 (normal, 36-page, adult) / ₹3,500 (Tatkaal)", timeline: "~30–45 days (normal), 1–3 days after police verification (Tatkaal)",
    documents: ["Proof of Address", "Proof of Date of Birth", "Aadhaar (recommended)", "Annexures for name/address change if applicable"],
    steps: [
      "Register and fill the online application at passportindia.gov.in.",
      "Pay the fee online and book an appointment at your nearest Passport Seva Kendra (PSK).",
      "Visit the PSK with original documents for verification and biometrics.",
      "Police verification is conducted (pre- or post-issuance depending on category).",
      "Passport is printed and dispatched by post once verification clears.",
    ],
  },
  {
    name: "Ration Card", desc: "Apply for a card to access subsidized food grains under the public distribution system.", portal: "State Food & Civil Supplies Department portal (varies by state)",
    legalBasis: "National Food Security Act, 2013", fee: "Nominal (₹5–₹45 depending on state)", timeline: "30–60 days after verification",
    documents: ["Aadhaar of all family members", "Proof of address", "Income certificate", "Family photograph", "Old ration card (if transferring/correcting)"],
    steps: [
      "Apply online via your state's Food & Civil Supplies portal or visit a Common Service Centre (CSC)/Fair Price Shop office.",
      "Fill the household details form and upload/attach required documents.",
      "Pay the nominal application fee.",
      "A local Food Inspector conducts a household verification visit.",
      "On approval, the card (or e-ration card) is issued and linked to your Aadhaar for PDS entitlements.",
    ],
  },
  {
    name: "GST Registration", desc: "Register a business for Goods & Services Tax and file returns.", portal: "gst.gov.in",
    legalBasis: "Central GST Act, 2017, Section 22", fee: "Free (government fee); professional/CA fees vary if assisted", timeline: "3–7 working days",
    documents: ["PAN of business/proprietor", "Aadhaar", "Proof of business address", "Bank account details", "Photograph", "Business constitution proof (partnership deed/incorporation certificate if applicable)"],
    steps: [
      "Check if your turnover crosses the registration threshold (₹40 lakh goods / ₹20 lakh services in most states).",
      "Submit Part A of the GST REG-01 form online with PAN, mobile, and email for OTP verification.",
      "Complete Part B with business details and upload documents.",
      "An Application Reference Number (ARN) is generated; a GST officer may raise queries.",
      "On approval, GSTIN and registration certificate are issued electronically.",
    ],
  },
  {
    name: "RTI Request", desc: "File a Right to Information application with a public authority.", portal: "rtionline.gov.in",
    legalBasis: "Right to Information Act, 2005, Section 6", fee: "₹10 (waived for BPL applicants)", timeline: "30 days for a response (48 hours if life/liberty is concerned)",
    documents: ["No supporting documents required — only the specific information sought"],
    steps: [
      "Identify the correct Public Authority and its Public Information Officer (PIO).",
      "Submit the request in writing or via rtionline.gov.in, clearly specifying the information sought.",
      "Pay the ₹10 fee (online or postal order/demand draft for offline applications).",
      "The PIO must respond within 30 days; if denied, you can file a First Appeal with the Appellate Authority.",
    ],
  },
  {
    name: "Driving Licence", desc: "Apply for a learner's or permanent licence, or renewal.", portal: "parivahan.gov.in",
    legalBasis: "Motor Vehicles Act, 1988", fee: "₹200–₹700 depending on licence type/state", timeline: "Learner's licence: same day (after test); permanent: 30 days after learner's licence",
    documents: ["Proof of age", "Proof of address", "Passport-size photographs", "Medical certificate (for transport licences)"],
    steps: [
      "Apply online for a Learner's Licence (LL) at parivahan.gov.in and book a slot for the online LL test.",
      "Pass the computer-based test on traffic rules to receive your LL, valid for 6 months.",
      "After 30 days (and before LL expiry), apply for a Permanent Driving Licence and book a practical driving test slot.",
      "Clear the driving test at the RTO; biometrics and photo are captured.",
      "Permanent licence is dispatched by post; also available as a DigiLocker e-document.",
    ],
  },
  {
    name: "Marriage Registration", desc: "Register a marriage under the applicable state Act.", portal: "State registration portal (varies)",
    legalBasis: "Hindu Marriage Act, 1955 (or the Special Marriage Act, 1954, for inter-faith marriages)", fee: "₹100–₹500 depending on state", timeline: "Same day to a few weeks depending on the Act invoked",
    documents: ["Proof of age and address of both spouses", "Marriage invitation card/proof of marriage ceremony", "Passport-size photographs", "Two witnesses with ID proof"],
    steps: [
      "Choose the applicable Act: Hindu Marriage Act (if the ceremony already took place) or Special Marriage Act (civil registration, including inter-faith marriages, with a 30-day public notice period).",
      "Apply online through your state's registration portal or visit the Sub-Registrar's office.",
      "Submit documents along with two witnesses.",
      "Appear in person before the Registrar on the scheduled date for verification and signatures.",
      "Receive the marriage certificate — issued same-day under the Hindu Marriage Act route in most states, or after the notice period under the Special Marriage Act.",
    ],
  },
  {
    name: "Consumer Complaint", desc: "File a complaint against a defective good or deficient service.", portal: "edaakhil.nic.in",
    legalBasis: "Consumer Protection Act, 2019, Section 35", fee: "Nominal court fee scaled to claim value (often waived up to ₹5 lakh)", timeline: "Varies by Commission workload; law prescribes disposal within 3–5 months where feasible",
    documents: ["Proof of purchase (invoice/receipt)", "Correspondence with the seller/service provider", "Warranty card if applicable", "ID proof"],
    steps: [
      "Send a written notice to the opposite party first, giving them a chance to resolve the issue.",
      "If unresolved, register on edaakhil.nic.in (e-Daakhil portal) for the appropriate Consumer Commission based on claim value.",
      "Upload your complaint, supporting documents, and pay the applicable fee.",
      "The Commission issues notice to the opposite party and schedules hearings.",
      "Attend hearings (in person or via authorized representative) until the Commission passes its order.",
    ],
  },
];


export default function NyayaSahayak() {
  const [dark, setDark] = useState(false);
  const [tab, setTab] = useState("chat");
  const [language, setLanguage] = useState("English");
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Namaste. I'm here to help you understand Indian laws, procedures, and your rights. Ask a question to begin — I'll cite the sections I rely on.", sources: [] },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [voiceError, setVoiceError] = useState("");
  const recognitionRef = useRef(null);
  const scrollRef = useRef(null);

  const speechSupported = typeof window !== "undefined" && (window.SpeechRecognition || window.webkitSpeechRecognition);

  function toggleListening() {
    if (!speechSupported) return;
    if (listening) {
      recognitionRef.current && recognitionRef.current.stop();
      setListening(false);
      return;
    }
    setVoiceError("");
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SR();
    recognition.lang = SPEECH_LOCALE[language] || "en-IN";
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.onresult = (event) => {
      let transcript = "";
      for (let i = 0; i < event.results.length; i++) transcript += event.results[i][0].transcript;
      setInput(transcript);
    };
    recognition.onerror = (event) => {
      const messages = {
        "not-allowed": "Microphone access was blocked. This embedded window may not have permission to use your mic — try opening this in its own browser tab.",
        "audio-capture": "No microphone was found on this device.",
        "network": "Voice recognition needs a network connection and none was reachable.",
        "no-speech": "Didn't catch any speech — try again.",
      };
      setVoiceError(messages[event.error] || `Voice input failed (${event.error}).`);
      setListening(false);
    };
    recognition.onend = () => setListening(false);
    recognitionRef.current = recognition;
    try {
      recognition.start();
      setListening(true);
    } catch (e) {
      setVoiceError("Couldn't start voice input in this environment.");
      setListening(false);
    }
  }

  const [docType, setDocType] = useState("affidavit");
  const [fields, setFields] = useState({});
  const [draft, setDraft] = useState("");
  const [draftLoading, setDraftLoading] = useState(false);

  const [elig, setElig] = useState({ income: "", category: "", answered: false, eligible: false, reason: "" });
  const [expandedService, setExpandedService] = useState(null);

  // --- Backend connection ---
  const [apiBaseUrl, setApiBaseUrl] = useState("http://localhost:8000");
  const [backendChatId, setBackendChatId] = useState(null);
  const [showSettings, setShowSettings] = useState(false);

  const connected = Boolean(apiBaseUrl);

  // Load any previously saved connection config from storage.
  useEffect(() => {
    (async () => {
      try {
        if (typeof window !== "undefined" && window.storage) {
          const res = await window.storage.get("nyaya-sahayak-config");
          if (res && res.value) {
            const cfg = JSON.parse(res.value);
            if (cfg.apiBaseUrl) setApiBaseUrl(cfg.apiBaseUrl);
          }
        } else if (typeof localStorage !== "undefined") {
          const value = localStorage.getItem("nyaya-sahayak-config");
          if (value) {
            const cfg = JSON.parse(value);
            if (cfg.apiBaseUrl) setApiBaseUrl(cfg.apiBaseUrl);
          }
        }
      } catch (e) {
        // no saved config yet — fine
      }
    })();
  }, []);

  async function persistConfig(next) {
    try {
      if (typeof window !== "undefined" && window.storage) {
        await window.storage.set("nyaya-sahayak-config", JSON.stringify(next), false);
      } else if (typeof localStorage !== "undefined") {
        localStorage.setItem("nyaya-sahayak-config", JSON.stringify(next));
      }
    } catch (e) {
      // non-fatal
    }
  }

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, loading]);

  const theme = dark
    ? { bg: "#14181F", panel: "#1C222B", panel2: "#242B36", ink: "#F2EFE6", sub: "#9AA5B1", accent: "#C6A15B", border: "#2E3644" }
    : { bg: "#F7F3EA", panel: "#FFFDF8", panel2: "#EFE9DA", ink: "#20242B", sub: "#5C6B73", accent: "#8A6A2F", border: "#DFD6BE" };

  async function sendMessage() {
    if (!input.trim() || loading) return;
    const q = input.trim();
    setInput("");
    setMessages(m => [...m, { role: "user", content: q, sources: [] }]);
    setLoading(true);
    const baseUrl = (apiBaseUrl || "http://localhost:8000").replace(/\/$/, "");
    try {
      const res = await fetch(`${baseUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: backendChatId, message: q, language }),
      });
      const chat = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(chat.detail || "The backend couldn't answer that.");
      setBackendChatId(chat.id);
      const last = chat.messages[chat.messages.length - 1];
      setMessages(m => [...m, {
        role: "assistant",
        content: last.content,
        sources: (last.sources || []).map(s => ({ act: s.act_name, section: s.section, text: s.text })),
        feedback: null,
        messageId: last.id,
      }]);
    } catch (e) {
      setMessages(m => [...m, { role: "assistant", content: e.message || "Something went wrong reaching the legal assistant. Please try again.", sources: [] }]);
    } finally {
      setLoading(false);
    }
  }

  function recordFeedback(index, rating) {
    setMessages(ms => ms.map((mm, mi) => mi === index ? { ...mm, feedback: rating } : mm));
    const baseUrl = (apiBaseUrl || "http://localhost:8000").replace(/\/$/, "");
    fetch(`${baseUrl}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message_id: messages[index]?.messageId || null, rating }),
    }).catch(() => {});
  }

  async function generateDraft() {
    setDraftLoading(true);
    setDraft("");
    try {
      const schema = DOC_TYPES[docType];
      const docTypeLabel = docType === "custom" ? (fields["Type of document"] || "Legal Document") : schema.label;
      const detailLines = schema.fields.map(f => `${f}: ${fields[f] || "(not provided)"}`).join("\n");
      const baseUrl = (apiBaseUrl || "http://localhost:8000").replace(/\/$/, "");

      const res = await fetch(`${baseUrl}/draft/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ doc_type: docTypeLabel, fields, language }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "The backend couldn't generate that draft.");
      setDraft(data.content);
    } catch (e) {
      setDraft(e.message || "Could not generate the draft. Please try again.");
    } finally {
      setDraftLoading(false);
    }
  }

  function downloadDraft() {
    const blob = new Blob([draft], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${DOC_TYPES[docType].label.replace(/\s+/g, "_")}_draft.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function checkEligibility() {
    const income = parseFloat(elig.income);
    const categoryFree = ["Woman", "Child", "SC/ST", "Person with disability", "Industrial workman", "Disaster/riot victim", "Senior citizen"].includes(elig.category);
    const incomeEligible = !isNaN(income) && income <= 300000;
    const eligible = categoryFree || incomeEligible;
    const reason = categoryFree
      ? `Persons in the "${elig.category}" category are entitled to free legal aid under Section 12 of the Legal Services Authorities Act, 1987, regardless of income.`
      : incomeEligible
      ? "Your stated annual income falls within the commonly applied free-legal-aid income threshold (varies slightly by state, generally around ₹3,00,000)."
      : "Based on what you've entered, you may not qualify for automatic free legal aid, but every District Legal Services Authority reviews applications individually — it's worth applying regardless.";
    setElig(e => ({ ...e, answered: true, eligible, reason }));
  }

  return (
    <div style={{ background: theme.bg, color: theme.ink, fontFamily: "'IBM Plex Sans', sans-serif" }} className="w-full h-screen overflow-hidden flex flex-col" >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
        .serif-display { font-family: 'Lora', serif; }
        .mono-cite { font-family: 'IBM Plex Mono', monospace; }
        .fade-in { animation: fadeIn 0.35s ease both; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
        ::selection { background: ${theme.accent}55; }
      `}</style>

      {/* Top ribbon */}
      <div style={{ borderBottom: `1px solid ${theme.border}`, background: theme.panel }} className="flex items-center justify-between px-5 py-3">
        <div className="flex items-center gap-2.5">
          <div style={{ background: theme.accent }} className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0">
            <Scale size={16} color={dark ? "#14181F" : "#FFFDF8"} />
          </div>
          <div>
            <div className="serif-display text-lg leading-none" style={{ color: theme.ink }}>Nyāya Sahāyak</div>
            <div className="text-[11px] tracking-wide uppercase" style={{ color: theme.sub }}>AI Legal Information Assistant</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div
            title="Connected to your local FastAPI backend"
            style={{ borderColor: theme.border, color: connected ? theme.accent : theme.sub }}
            className="hidden md:flex items-center gap-1.5 text-[10px] border rounded-full px-2 py-1"
          >
            <Server size={10} />
            {connected ? "Connected" : "Disconnected"}
          </div>
          <select value={language} onChange={e => setLanguage(e.target.value)} style={{ background: theme.panel2, color: theme.ink, borderColor: theme.border }} className="text-xs rounded-md border px-2 py-1.5 outline-none">
            {LANGUAGES.map(l => <option key={l}>{l}</option>)}
          </select>
          <button onClick={() => setDark(d => !d)} style={{ background: theme.panel2, borderColor: theme.border }} className="rounded-md border p-1.5">
            {dark ? <Sun size={15} color={theme.ink} /> : <Moon size={15} color={theme.ink} />}
          </button>
          <button onClick={() => setShowSettings(s => !s)} style={{ background: showSettings ? theme.accent : theme.panel2, borderColor: theme.border }} className="rounded-md border p-1.5">
            <Settings size={15} color={showSettings ? (dark ? "#14181F" : "#FFFDF8") : theme.ink} />
          </button>
        </div>
      </div>

      {showSettings && (
        <div style={{ background: theme.panel, borderBottom: `1px solid ${theme.border}` }} className="px-5 py-4 fade-in">
          <div className="flex items-center justify-between mb-3">
            <div className="serif-display text-sm">Backend Connection</div>
            <button onClick={() => setShowSettings(false)} style={{ color: theme.sub }}><X size={15} /></button>
          </div>
          <div className="max-w-sm space-y-2.5">
            <div>
              <label className="text-[11px] uppercase tracking-wide" style={{ color: theme.sub }}>Backend API URL</label>
              <input
                value={apiBaseUrl}
                onChange={e => setApiBaseUrl(e.target.value)}
                onBlur={() => persistConfig({ apiBaseUrl })}
                placeholder="http://localhost:8000"
                style={{ background: theme.panel2, color: theme.ink, borderColor: theme.border }}
                className="w-full rounded-md border px-2.5 py-1.5 text-[13px] mt-1 outline-none"
              />
              <div className="text-[11px] mt-1" style={{ color: theme.sub }}>Configure the URL of the local FastAPI server.</div>
            </div>
          </div>
        </div>
      )}

      {/* Disclaimer strip */}
      <div style={{ background: dark ? "#3A2A2A" : "#F3E6DD", borderBottom: `1px solid ${theme.border}` }} className="flex items-center gap-2 px-5 py-2 text-xs">
        <Stamp size={13} style={{ color: theme.accent, flexShrink: 0 }} />
        <span style={{ color: theme.sub }}>Informational only, not legal advice. For your specific situation, consult a licensed advocate.</span>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div style={{ borderRight: `1px solid ${theme.border}`, background: theme.panel }} className="w-44 flex-shrink-0 py-3 hidden sm:flex sm:flex-col overflow-y-auto">
          {[
            { id: "chat", label: "Ask a Question", icon: MessageSquare },
            { id: "draft", label: "Draft Documents", icon: FileText },
            { id: "eligibility", label: "Legal Aid Check", icon: ClipboardCheck },
            { id: "services", label: "Govt. Services", icon: Landmark },
          ].map(item => (
            <button
              key={item.id}
              onClick={() => setTab(item.id)}
              style={{
                color: tab === item.id ? theme.accent : theme.sub,
                borderLeft: tab === item.id ? `2px solid ${theme.accent}` : "2px solid transparent",
                background: tab === item.id ? theme.panel2 : "transparent",
              }}
              className="w-full flex items-center gap-2 px-4 py-2.5 text-[13px] text-left"
            >
              <item.icon size={14} />
              {item.label}
            </button>
          ))}
        </div>

        {/* Main panel */}
        <div className="flex-1 flex flex-col">
          {tab === "chat" && (
            <>
              <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
                {messages.map((m, i) => (
                  <div key={i} className="fade-in">
                    <div className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                      <div
                        style={{
                          background: m.role === "user" ? theme.accent : theme.panel2,
                          color: m.role === "user" ? (dark ? "#14181F" : "#FFFDF8") : theme.ink,
                          maxWidth: "78%",
                        }}
                        className="rounded-lg px-3.5 py-2.5 text-[13.5px] leading-relaxed whitespace-pre-wrap"
                      >
                        {m.content}
                      </div>
                    </div>
                    {m.role === "assistant" && m.sources && m.sources.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-1.5 ml-0.5">
                        {m.sources.map((s, si) => (
                          <span key={si} style={{ borderColor: theme.accent, color: theme.accent }} className="mono-cite text-[10px] border rounded px-1.5 py-0.5">
                            {s.act} — {s.section}
                          </span>
                        ))}
                      </div>
                    )}
                    {m.role === "assistant" && i > 0 && (
                      <div className="flex gap-2 mt-1.5 ml-0.5">
                        <button onClick={() => recordFeedback(i, "up")} style={{ color: m.feedback === "up" ? theme.accent : theme.sub }}>
                          <ThumbsUp size={12} />
                        </button>
                        <button onClick={() => recordFeedback(i, "down")} style={{ color: m.feedback === "down" ? theme.accent : theme.sub }}>
                          <ThumbsDown size={12} />
                        </button>
                      </div>
                    )}
                  </div>
                ))}
                {loading && (
                  <div className="flex items-center gap-2 text-xs" style={{ color: theme.sub }}>
                    <Loader2 size={13} className="animate-spin" /> Retrieving relevant sections…
                  </div>
                )}
              </div>
              <div style={{ borderTop: `1px solid ${theme.border}` }} className="flex items-center gap-2 px-4 py-3">
                <button
                  onClick={toggleListening}
                  disabled={!speechSupported}
                  title={speechSupported ? (listening ? "Stop recording" : "Speak your question") : "Voice input isn't supported in this browser — try Chrome"}
                  style={{
                    background: listening ? "#B03A3A" : theme.panel2,
                    borderColor: theme.border,
                    opacity: speechSupported ? 1 : 0.4,
                  }}
                  className="rounded-md border p-2.5 flex-shrink-0"
                >
                  {listening ? <MicOff size={15} color="#FFFDF8" /> : <Mic size={15} color={theme.ink} />}
                </button>
                <input
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && sendMessage()}
                  placeholder={listening ? "Listening…" : "e.g. How do I file a consumer complaint?"}
                  style={{ background: theme.panel2, color: theme.ink, borderColor: theme.border }}
                  className="flex-1 rounded-md border px-3 py-2 text-[13px] outline-none"
                />
                <button onClick={sendMessage} disabled={loading} style={{ background: theme.accent }} className="rounded-md p-2.5 disabled:opacity-50 flex-shrink-0">
                  <Send size={15} color={dark ? "#14181F" : "#FFFDF8"} />
                </button>
              </div>
              {voiceError && (
                <div className="px-4 pb-2 text-[11px]" style={{ color: "#B03A3A" }}>{voiceError}</div>
              )}
            </>
          )}

          {tab === "draft" && (
            <div className="p-5 overflow-y-auto flex-1">
              <div className="serif-display text-base mb-3">Generate a Document Draft</div>
              <div className="flex flex-wrap gap-1.5 mb-4">
                {Object.entries(DOC_TYPES).map(([key, d]) => (
                  <button
                    key={key}
                    onClick={() => { setDocType(key); setFields({}); setDraft(""); }}
                    style={{
                      background: docType === key ? theme.accent : theme.panel2,
                      color: docType === key ? (dark ? "#14181F" : "#FFFDF8") : theme.ink,
                      borderColor: theme.border,
                    }}
                    className="text-xs rounded-full border px-3 py-1.5"
                  >
                    {d.label}
                  </button>
                ))}
              </div>
              <div className="grid sm:grid-cols-2 gap-3 mb-4">
                {DOC_TYPES[docType].fields.map(f => (
                  <div key={f}>
                    <label className="text-[11px] uppercase tracking-wide" style={{ color: theme.sub }}>{f}</label>
                    <input
                      value={fields[f] || ""}
                      onChange={e => setFields(v => ({ ...v, [f]: e.target.value }))}
                      style={{ background: theme.panel2, color: theme.ink, borderColor: theme.border }}
                      className="w-full rounded-md border px-2.5 py-1.5 text-[13px] mt-1 outline-none"
                    />
                  </div>
                ))}
              </div>
              <button onClick={generateDraft} disabled={draftLoading} style={{ background: theme.accent }} className="rounded-md px-4 py-2 text-[13px] disabled:opacity-50 flex items-center gap-2" >
                {draftLoading && <Loader2 size={13} className="animate-spin" />}
                <span style={{ color: dark ? "#14181F" : "#FFFDF8" }}>Generate Draft</span>
              </button>

              {draft && (
                <div className="mt-4 fade-in">
                  <div style={{ background: theme.panel2, borderColor: theme.border }} className="rounded-md border p-4 text-[12.5px] whitespace-pre-wrap leading-relaxed max-h-72 overflow-y-auto">
                    {draft}
                  </div>
                  <button onClick={downloadDraft} style={{ borderColor: theme.accent, color: theme.accent }} className="mt-2 flex items-center gap-1.5 text-xs border rounded-md px-3 py-1.5">
                    <Download size={13} /> Download .txt
                  </button>
                </div>
              )}
            </div>
          )}

          {tab === "eligibility" && (
            <div className="p-5">
              <div className="serif-display text-base mb-3">Free Legal Aid Eligibility Check</div>
              <div className="space-y-3 max-w-sm">
                <div>
                  <label className="text-[11px] uppercase tracking-wide" style={{ color: theme.sub }}>Annual family income (₹)</label>
                  <input value={elig.income} onChange={e => setElig(v => ({ ...v, income: e.target.value }))} style={{ background: theme.panel2, color: theme.ink, borderColor: theme.border }} className="w-full rounded-md border px-2.5 py-1.5 text-[13px] mt-1 outline-none" />
                </div>
                <div>
                  <label className="text-[11px] uppercase tracking-wide" style={{ color: theme.sub }}>Do any of these apply to you?</label>
                  <select value={elig.category} onChange={e => setElig(v => ({ ...v, category: e.target.value }))} style={{ background: theme.panel2, color: theme.ink, borderColor: theme.border }} className="w-full rounded-md border px-2.5 py-1.5 text-[13px] mt-1 outline-none">
                    <option value="">None of these</option>
                    <option>Woman</option><option>Child</option><option>SC/ST</option>
                    <option>Person with disability</option><option>Industrial workman</option>
                    <option>Disaster/riot victim</option><option>Senior citizen</option>
                  </select>
                </div>
                <button onClick={checkEligibility} style={{ background: theme.accent }} className="rounded-md px-4 py-2 text-[13px]">
                  <span style={{ color: dark ? "#14181F" : "#FFFDF8" }}>Check Eligibility</span>
                </button>
              </div>
              {elig.answered && (
                <div style={{ background: theme.panel2, borderColor: theme.accent }} className="mt-4 max-w-md border-l-2 rounded-md p-3 text-[13px] fade-in">
                  <div className="font-medium mb-1" style={{ color: elig.eligible ? theme.accent : theme.sub }}>
                    {elig.eligible ? "You are likely eligible for free legal aid." : "Automatic eligibility not indicated."}
                  </div>
                  <div style={{ color: theme.sub }}>{elig.reason}</div>
                </div>
              )}
            </div>
          )}

          {tab === "services" && (
            <div className="p-5 overflow-y-auto flex-1">
              <div className="serif-display text-base mb-1">Government Services Guide</div>
              <div className="text-xs mb-3" style={{ color: theme.sub }}>Tap a document to see the required papers, fees, and step-by-step process.</div>
              <div className="grid sm:grid-cols-2 gap-3">
                {GOV_SERVICES.map(s => {
                  const isOpen = expandedService === s.name;
                  return (
                    <div key={s.name} style={{ background: theme.panel2, borderColor: isOpen ? theme.accent : theme.border }} className={`rounded-md border p-3 ${isOpen ? "sm:col-span-2" : "sm:col-span-1"}`} >
                      <button onClick={() => setExpandedService(isOpen ? null : s.name)} className="w-full text-left">
                        <div className="flex items-start justify-between gap-2">
                          <div className="text-[13.5px] font-medium">{s.name}</div>
                          <span className="mono-cite text-[10px] flex-shrink-0" style={{ color: theme.accent }}>{isOpen ? "− hide" : "+ steps"}</span>
                        </div>
                        <div className="text-xs mt-1" style={{ color: theme.sub }}>{s.desc}</div>
                        <div className="mono-cite text-[10px] mt-2" style={{ color: theme.accent }}>{s.portal}</div>
                      </button>

                      {isOpen && (
                        <div className="mt-3 pt-3 fade-in" style={{ borderTop: `1px solid ${theme.border}` }}>
                          <div className="text-[10px] uppercase tracking-wide mb-1" style={{ color: theme.sub }}>Legal basis</div>
                          <div className="mono-cite text-[11px] mb-2.5" style={{ color: theme.ink }}>{s.legalBasis}</div>

                          <div className="flex gap-3 mb-2.5 flex-wrap">
                            <div style={{ borderColor: theme.border }} className="border rounded px-2 py-1 text-[11px]">
                              <span style={{ color: theme.sub }}>Fee: </span>{s.fee}
                            </div>
                            <div style={{ borderColor: theme.border }} className="border rounded px-2 py-1 text-[11px]">
                              <span style={{ color: theme.sub }}>Timeline: </span>{s.timeline}
                            </div>
                          </div>

                          <div className="text-[10px] uppercase tracking-wide mb-1" style={{ color: theme.sub }}>Documents required</div>
                          <ul className="text-[12px] mb-2.5 space-y-0.5 list-disc list-inside" style={{ color: theme.ink }}>
                            {s.documents.map((d, di) => <li key={di}>{d}</li>)}
                          </ul>

                          <div className="text-[10px] uppercase tracking-wide mb-1" style={{ color: theme.sub }}>Steps</div>
                          <ol className="text-[12px] space-y-1.5">
                            {s.steps.map((step, si) => (
                              <li key={si} className="flex gap-2">
                                <span style={{ color: theme.accent }} className="mono-cite flex-shrink-0">{si + 1}.</span>
                                <span style={{ color: theme.ink }}>{step}</span>
                              </li>
                            ))}
                          </ol>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
