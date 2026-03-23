import { useState } from "react";

const API_URL = "http://localhost:5000/api/costing";

const SUPPORTED_KW = [500, 1000, 1500, 2000, 2500, 3000, 4500, 6000];
const DEFAULT_BLOWER_HP = { 500:10, 1000:10, 1500:15, 2000:20, 2500:25, 3000:25, 4500:40, 6000:60 };
const DEFAULT_SPM = { 500:1.8, 1000:1.8, 1500:1.8, 2000:1.8, 2500:1.8, 3000:1.8, 4500:1.8, 6000:2.0 };

const SECTIONS = [
  "Burner & Pilot", "Gas Line - Pilot", "Gas Line - Burner",
  "Air Line - UV/Pilot", "Air Line - Burner", "Temperature Control",
  "Blower", "Controls & Gas Train"
];

const fmt = (n) => new Intl.NumberFormat("en-IN").format(Math.round(n));

const inp = {
  width: "100%", padding: "12px 16px", fontSize: 15,
  border: "1px solid #e2e8f0", borderRadius: 10,
  background: "#f1f5f9", color: "#1e293b", outline: "none",
  boxSizing: "border-box", fontFamily: "inherit",
  appearance: "none", WebkitAppearance: "none",
};
const lbl = { display: "block", marginBottom: 6, fontSize: 14, color: "#475569", fontWeight: 500 };

export default function App() {
  const [step, setStep] = useState(1);

  // Step 1
  const [companyName, setCompanyName] = useState("");
  const [companyAddress, setCompanyAddress] = useState("");
  const [project, setProject] = useState("Ladle Preheater");

  // Step 2
  const [kw, setKw] = useState(1000);
  const [spm, setSpm] = useState(1.8);
  const [numPairs, setNumPairs] = useState(2);
  const [blowerHp, setBlowerHp] = useState(10);
  const [thermoType, setThermoType] = useState("K");
  const [pipelineCost, setPipelineCost] = useState(0);

  // Step 3
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeSection, setActiveSection] = useState(null);

  // When KW changes, update blower HP and SPM defaults
  const handleKwChange = (newKw) => {
    setKw(newKw);
    setBlowerHp(DEFAULT_BLOWER_HP[newKw]);
    setSpm(DEFAULT_SPM[newKw]);
  };

  const generateCosting = async (exportSheets = false) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          kw,
          selling_price_multiplier: spm,
          num_pairs: numPairs,
          blower_hp: blowerHp,
          thermocouple_type: thermoType,
          pipeline_cost_extra: pipelineCost,
          company_name: companyName,
          company_address: companyAddress,
          project,
          export_to_sheets: exportSheets,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Something went wrong");
      setResult(data);
      setActiveSection(null);
      setStep(3);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredRows = result
    ? activeSection !== null
      ? result.items.filter(r => r.section === activeSection)
      : result.items
    : [];

  const reset = () => {
    setStep(1); setResult(null); setError(null);
    setCompanyName(""); setCompanyAddress(""); setActiveSection(null);
  };

  return (
    <div style={{ fontFamily: "'Segoe UI', system-ui, sans-serif", background: "#fff", minHeight: "100vh", color: "#1e293b" }}>

      {/* Topbar */}
      <div style={{ borderBottom: "1px solid #e2e8f0", padding: "0 40px", display: "flex", alignItems: "center", height: 56, background: "#fff" }}>
        <span style={{ fontWeight: 700, fontSize: 16, color: "#1e293b" }}>REGEN Systems</span>
        <div style={{ display: "flex", gap: 4, marginLeft: "auto", background: "#f1f5f9", borderRadius: 8, padding: 4 }}>
          {["Customer Details", "Parameters", "Cost Sheet"].map((label, i) => {
            const s = i + 1;
            return (
              <button key={s} onClick={() => s <= step ? setStep(s) : null}
                style={{ padding: "6px 16px", fontSize: 13, fontFamily: "inherit", cursor: s <= step ? "pointer" : "default",
                  background: step === s ? "#fff" : "transparent",
                  color: step === s ? "#1e40af" : s < step ? "#475569" : "#94a3b8",
                  border: "none", borderRadius: 6, fontWeight: step === s ? 600 : 400,
                  boxShadow: step === s ? "0 1px 4px rgba(0,0,0,0.1)" : "none", transition: "all 0.15s" }}>
                {s < step ? "✓ " : ""}{label}
              </button>
            );
          })}
        </div>
      </div>

      <div style={{ maxWidth: 680, margin: "0 auto", padding: "48px 24px 100px" }}>

        {/* ── STEP 1 ── */}
        {step === 1 && (
          <div>
            <h1 style={{ fontSize: 34, fontWeight: 800, marginBottom: 6, color: "#0f172a", letterSpacing: "-0.5px" }}>Offer Generator</h1>
            <p style={{ color: "#64748b", marginBottom: 44, fontSize: 15, lineHeight: 1.6 }}>
              Generate a detailed cost sheet for REGEN Burner systems — 500 KW to 6000 KW.
            </p>

            <h2 style={{ fontSize: 20, fontWeight: 700, color: "#0f172a", marginBottom: 28, paddingBottom: 14, borderBottom: "1px solid #f1f5f9" }}>
              Step 1: Customer & Organization Details
            </h2>

            <div style={{ marginBottom: 24 }}>
              <label style={lbl}>Company Name</label>
              <input style={inp} placeholder="e.g. Tata Steel" value={companyName} onChange={e => setCompanyName(e.target.value)} />
            </div>

            <div style={{ marginBottom: 24 }}>
              <label style={lbl}>Company Address</label>
              <textarea style={{ ...inp, minHeight: 96, resize: "vertical" }} placeholder="e.g. Mumbai, Maharashtra"
                value={companyAddress} onChange={e => setCompanyAddress(e.target.value)} />
            </div>

            <div style={{ marginBottom: 24 }}>
              <label style={lbl}>Project</label>
              <div style={{ position: "relative" }}>
                <select style={inp} value={project} onChange={e => setProject(e.target.value)}>
                  {["Ladle Preheater", "Furnace", "Boiler", "Heat Treatment", "Forging", "Custom"].map(p => <option key={p}>{p}</option>)}
                </select>
                <span style={{ position: "absolute", right: 14, top: "50%", transform: "translateY(-50%)", pointerEvents: "none", color: "#94a3b8", fontSize: 11 }}>▼</span>
              </div>
            </div>

            <button onClick={() => setStep(2)}
              style={{ width: "100%", padding: "14px", background: "#1e40af", border: "none", borderRadius: 10,
                color: "#fff", fontFamily: "inherit", fontWeight: 700, fontSize: 15, cursor: "pointer", marginTop: 12 }}>
              Next Step →
            </button>
          </div>
        )}

        {/* ── STEP 2 ── */}
        {step === 2 && (
          <div>
            <h1 style={{ fontSize: 34, fontWeight: 800, marginBottom: 6, color: "#0f172a", letterSpacing: "-0.5px" }}>Costing Parameters</h1>
            <p style={{ color: "#64748b", marginBottom: 44, fontSize: 15 }}>Configure the technical and commercial parameters.</p>

            <h2 style={{ fontSize: 20, fontWeight: 700, color: "#0f172a", marginBottom: 28, paddingBottom: 14, borderBottom: "1px solid #f1f5f9" }}>
              Step 2: System Configuration
            </h2>

            {/* KW Selector */}
            <div style={{ marginBottom: 28 }}>
              <label style={lbl}>Burner Power Rating (KW)</label>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                {SUPPORTED_KW.map(v => (
                  <button key={v} onClick={() => handleKwChange(v)}
                    style={{ flex: "1 1 calc(25% - 8px)", padding: "13px 8px", borderRadius: 10, border: "1px solid", cursor: "pointer",
                      fontSize: 15, fontFamily: "inherit", fontWeight: 700, transition: "all 0.15s",
                      background: kw === v ? "#1e40af" : "#f1f5f9",
                      borderColor: kw === v ? "#1e40af" : "#e2e8f0",
                      color: kw === v ? "#fff" : "#64748b" }}>
                    {v} KW
                  </button>
                ))}
              </div>
            </div>

            {/* SPM */}
            <div style={{ marginBottom: 28 }}>
              <label style={lbl}>Selling Price Multiplier</label>
              <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                <input type="range" min={1} max={3} step={0.1} value={spm}
                  onChange={e => setSpm(parseFloat(e.target.value))}
                  style={{ flex: 1, accentColor: "#1e40af", cursor: "pointer" }} />
                <div style={{ ...inp, width: 76, textAlign: "center", flexShrink: 0, padding: "10px 8px", fontWeight: 700, color: "#1e40af", fontSize: 16 }}>
                  {spm.toFixed(1)}x
                </div>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#94a3b8", marginTop: 4 }}>
                <span>1.0x</span><span>3.0x</span>
              </div>
            </div>

            {/* Num Pairs */}
            <div style={{ marginBottom: 28 }}>
              <label style={lbl}>Number of Burner Pairs</label>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <button onClick={() => setNumPairs(Math.max(1, numPairs - 1))}
                  style={{ width: 44, height: 44, borderRadius: 10, border: "1px solid #e2e8f0", background: "#f1f5f9",
                    fontSize: 20, cursor: "pointer", fontFamily: "inherit", color: "#475569", flexShrink: 0 }}>
                  -
                </button>
                <input type="number" min={1} max={50} value={numPairs}
                  onChange={e => setNumPairs(Math.max(1, parseInt(e.target.value) || 1))}
                  style={{ ...inp, textAlign: "center", fontWeight: 700, fontSize: 18, color: "#1e40af" }} />
                <button onClick={() => setNumPairs(Math.min(50, numPairs + 1))}
                  style={{ width: 44, height: 44, borderRadius: 10, border: "1px solid #e2e8f0", background: "#f1f5f9",
                    fontSize: 20, cursor: "pointer", fontFamily: "inherit", color: "#475569", flexShrink: 0 }}>
                  +
                </button>
              </div>
              <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 6 }}>
                Standard: 2 pairs &nbsp;·&nbsp; Enter any value from 1 to 50
              </div>
            </div>

            {/* Blower HP */}
            <div style={{ marginBottom: 28 }}>
              <label style={lbl}>
                Combustion Blower HP
                <span style={{ marginLeft: 8, fontSize: 12, color: "#94a3b8", fontWeight: 400 }}>
                  (default for {kw} KW: {DEFAULT_BLOWER_HP[kw]} HP)
                </span>
              </label>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {[5, 7.5, 10, 15, 20, 25, 30, 40, 50, 60].map(v => (
                  <button key={v} onClick={() => setBlowerHp(v)}
                    style={{ padding: "10px 14px", borderRadius: 8, border: "1px solid", cursor: "pointer",
                      fontSize: 14, fontFamily: "inherit", transition: "all 0.15s",
                      background: blowerHp === v ? "#1e40af" : "#f1f5f9",
                      borderColor: blowerHp === v ? "#1e40af" : "#e2e8f0",
                      color: blowerHp === v ? "#fff" : "#64748b", fontWeight: blowerHp === v ? 600 : 400 }}>
                    {v} HP
                  </button>
                ))}
              </div>
            </div>

            {/* Thermocouple */}
            <div style={{ marginBottom: 28 }}>
              <label style={lbl}>Thermocouple Type</label>
              <div style={{ display: "flex", gap: 12 }}>
                {[["K", "Standard", "Rs. 5,000 / unit"], ["R", "High Temperature", "Rs. 25,000 / unit"]].map(([v, title, sub]) => (
                  <button key={v} onClick={() => setThermoType(v)}
                    style={{ flex: 1, padding: "14px 16px", borderRadius: 10, border: "1px solid", cursor: "pointer",
                      fontFamily: "inherit", transition: "all 0.15s", textAlign: "left",
                      background: thermoType === v ? "#eff6ff" : "#f1f5f9",
                      borderColor: thermoType === v ? "#1e40af" : "#e2e8f0" }}>
                    <div style={{ fontWeight: 700, fontSize: 15, color: thermoType === v ? "#1e40af" : "#475569" }}>Type {v}</div>
                    <div style={{ fontSize: 13, color: "#64748b", marginTop: 2 }}>{title}</div>
                    <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 2 }}>{sub}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Pipeline cost */}
            <div style={{ marginBottom: 28 }}>
              <label style={lbl}>Pipeline Cost Extra (Rs.)</label>
              <div style={{ position: "relative" }}>
                <span style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "#94a3b8", fontSize: 14, fontWeight: 500 }}>Rs.</span>
                <input type="number" style={{ ...inp, paddingLeft: 46 }} placeholder="0"
                  value={pipelineCost || ""} onChange={e => setPipelineCost(Number(e.target.value))} />
              </div>
            </div>

            {error && (
              <div style={{ background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 10, padding: "12px 16px", marginBottom: 20, color: "#dc2626", fontSize: 14 }}>
                Error: {error}
              </div>
            )}

            <div style={{ display: "flex", gap: 12, marginTop: 12 }}>
              <button onClick={() => setStep(1)}
                style={{ padding: "14px 24px", background: "#f1f5f9", border: "1px solid #e2e8f0", borderRadius: 10,
                  color: "#475569", fontFamily: "inherit", fontWeight: 600, fontSize: 15, cursor: "pointer" }}>
                ← Back
              </button>
              <button onClick={() => generateCosting(false)} disabled={loading}
                style={{ flex: 1, padding: "14px", background: loading ? "#93c5fd" : "#1e40af", border: "none", borderRadius: 10,
                  color: "#fff", fontFamily: "inherit", fontWeight: 700, fontSize: 15,
                  cursor: loading ? "not-allowed" : "pointer", transition: "background 0.2s" }}>
                {loading ? "Generating..." : "Generate Cost Sheet →"}
              </button>
            </div>
          </div>
        )}

        {/* ── STEP 3 ── */}
        {step === 3 && result && (
          <div>
            <h1 style={{ fontSize: 34, fontWeight: 800, marginBottom: 6, color: "#0f172a", letterSpacing: "-0.5px" }}>Cost Sheet</h1>
            {companyName && (
              <p style={{ color: "#475569", marginBottom: 4, fontSize: 15, fontWeight: 500 }}>
                {companyName}{companyAddress ? ` · ${companyAddress}` : ""}
              </p>
            )}
            <p style={{ color: "#94a3b8", marginBottom: 36, fontSize: 13 }}>
              REGEN {kw} KW &nbsp;·&nbsp; {numPairs} pair{numPairs > 1 ? "s" : ""}
              &nbsp;·&nbsp; {spm}x markup &nbsp;·&nbsp; {blowerHp} HP blower
              &nbsp;·&nbsp; Type {thermoType} thermocouple &nbsp;·&nbsp; {project}
            </p>

            {/* Summary Cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 14, marginBottom: 32 }}>
              {[
                { label: "Total Cost Price",    value: `Rs. ${fmt(result.summary.total_cost)}`,  sub: `${(result.summary.total_cost / 100000).toFixed(1)} Lakhs`,         hi: false },
                { label: "Total Selling Price", value: `Rs. ${fmt(result.summary.total_sell)}`,  sub: `${(result.summary.total_sell / 100000).toFixed(1)} Lakhs`,         hi: false },
                { label: "Grand Total",         value: `Rs. ${fmt(result.summary.grand_total)}`, sub: `${result.summary.grand_total_lakhs} Lakhs`, hi: true  },
              ].map(c => (
                <div key={c.label} style={{ border: `1.5px solid ${c.hi ? "#1e40af" : "#e2e8f0"}`, borderRadius: 12, padding: "16px 18px", background: c.hi ? "#eff6ff" : "#f8fafc" }}>
                  <div style={{ fontSize: 11, color: "#94a3b8", textTransform: "uppercase", letterSpacing: 0.8, marginBottom: 6 }}>{c.label}</div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: c.hi ? "#1e40af" : "#1e293b" }}>{c.value}</div>
                  <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 3 }}>{c.sub}</div>
                </div>
              ))}
            </div>

            {/* Section filter chips */}
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 18 }}>
              {["All Items", ...SECTIONS].map((s, i) => {
                const idx = i === 0 ? null : i - 1;
                const active = activeSection === idx;
                return (
                  <button key={s} onClick={() => setActiveSection(idx)}
                    style={{ padding: "6px 14px", borderRadius: 20, border: "1px solid", cursor: "pointer",
                      fontFamily: "inherit", fontSize: 12, fontWeight: active ? 600 : 400, transition: "all 0.15s",
                      background: active ? "#1e40af" : "#f1f5f9",
                      borderColor: active ? "#1e40af" : "#e2e8f0",
                      color: active ? "#fff" : "#64748b" }}>
                    {s}
                  </button>
                );
              })}
            </div>

            {/* Table */}
            <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, overflow: "hidden", marginBottom: 32 }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr style={{ background: "#f8fafc" }}>
                    {["#", "Description", "Size", "Qty", "Cost/Unit", "Total Cost", "Selling Price"].map((h, i) => (
                      <th key={h} style={{ padding: "11px 14px", textAlign: i >= 3 ? "right" : "left",
                        color: "#64748b", fontWeight: 600, fontSize: 11, textTransform: "uppercase",
                        letterSpacing: 0.5, borderBottom: "1px solid #e2e8f0", whiteSpace: "nowrap" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filteredRows.map((row, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid #f1f5f9", background: i % 2 === 0 ? "#fff" : "#fafafa" }}>
                      <td style={{ padding: "10px 14px", color: "#cbd5e1", fontSize: 12 }}>{i + 1}</td>
                      <td style={{ padding: "10px 14px", color: "#1e293b" }}>{row.description}</td>
                      <td style={{ padding: "10px 14px", color: "#64748b" }}>{row.size}</td>
                      <td style={{ padding: "10px 14px", textAlign: "right", color: "#64748b" }}>{row.qty}</td>
                      <td style={{ padding: "10px 14px", textAlign: "right", color: "#64748b" }}>Rs. {fmt(row.cost_unit)}</td>
                      <td style={{ padding: "10px 14px", textAlign: "right", color: "#475569" }}>Rs. {fmt(row.total_cost)}</td>
                      <td style={{ padding: "10px 14px", textAlign: "right", color: "#1e293b", fontWeight: 600 }}>Rs. {fmt(row.total_sell)}</td>
                    </tr>
                  ))}

                  {activeSection === null && (
                    <>
                      <tr style={{ background: "#f8fafc", borderTop: "2px solid #e2e8f0" }}>
                        <td colSpan={5} style={{ padding: "11px 14px", color: "#64748b", fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: 1 }}>Subtotal</td>
                        <td style={{ padding: "11px 14px", textAlign: "right", color: "#475569", fontWeight: 600 }}>Rs. {fmt(result.summary.total_cost)}</td>
                        <td style={{ padding: "11px 14px", textAlign: "right", color: "#1e293b", fontWeight: 600 }}>Rs. {fmt(result.summary.total_sell)}</td>
                      </tr>
                      {pipelineCost > 0 && (
                        <tr style={{ background: "#f8fafc" }}>
                          <td colSpan={6} style={{ padding: "10px 14px", color: "#64748b", fontSize: 13 }}>Pipeline Cost Extra</td>
                          <td style={{ padding: "10px 14px", textAlign: "right", color: "#475569" }}>Rs. {fmt(pipelineCost)}</td>
                        </tr>
                      )}
                      <tr style={{ background: "#eff6ff", borderTop: "2px solid #bfdbfe" }}>
                        <td colSpan={6} style={{ padding: "14px", color: "#1e40af", fontWeight: 700, fontSize: 15 }}>Grand Total (Rounded)</td>
                        <td style={{ padding: "14px", textAlign: "right", color: "#1e40af", fontWeight: 700, fontSize: 17 }}>Rs. {fmt(result.summary.grand_total)}</td>
                      </tr>
                    </>
                  )}
                </tbody>
              </table>
            </div>

            <div style={{ display: "flex", gap: 12 }}>
              <button onClick={() => setStep(2)}
                style={{ padding: "14px 24px", background: "#f1f5f9", border: "1px solid #e2e8f0", borderRadius: 10,
                  color: "#475569", fontFamily: "inherit", fontWeight: 600, fontSize: 15, cursor: "pointer" }}>
                ← Back
              </button>
              <button onClick={() => generateCosting(true)} disabled={loading}
                style={{ flex: 1, padding: "14px", background: loading ? "#86efac" : "#16a34a", border: "none", borderRadius: 10,
                  color: "#fff", fontFamily: "inherit", fontWeight: 700, fontSize: 15,
                  cursor: loading ? "not-allowed" : "pointer", transition: "background 0.2s" }}>
                {loading ? "Exporting..." : "📤 Export to Google Sheets"}
              </button>
              <button onClick={reset}
                style={{ flex: 1, padding: "14px", background: "#1e40af", border: "none", borderRadius: 10,
                  color: "#fff", fontFamily: "inherit", fontWeight: 700, fontSize: 15, cursor: "pointer" }}>
                + New Offer
              </button>
            </div>

            {/* Google Sheet link */}
            {result.sheet && (
              <div style={{ marginTop: 16, padding: "16px 20px", background: "#f0fdf4", border: "1px solid #bbf7d0",
                borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: "#16a34a" }}>Google Sheet created!</div>
                  <div style={{ fontSize: 12, color: "#64748b", marginTop: 2 }}>{result.sheet.title}</div>
                </div>
                <a href={result.sheet.url} target="_blank" rel="noreferrer"
                  style={{ padding: "8px 16px", background: "#16a34a", color: "#fff", borderRadius: 8,
                    textDecoration: "none", fontSize: 13, fontWeight: 600 }}>
                  Open Sheet →
                </a>
              </div>
            )}
            {result.sheet_error && (
              <div style={{ marginTop: 16, padding: "12px 16px", background: "#fef2f2", border: "1px solid #fecaca",
                borderRadius: 10, color: "#dc2626", fontSize: 13 }}>
                Sheet export failed: {result.sheet_error}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}