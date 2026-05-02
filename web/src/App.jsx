import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "/evaluate";

export default function App() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [domain, setDomain] = useState("finance_v1");

  async function handleEvaluate() {
    setLoading(true);
    setError(null);
    setResult(null);

    const payload = {
      domain,
      structured_metrics: { cash_months: 0.5, debt_ratio: 0.4 },
      user_declared: { stress_level: 8 }
    };

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`HTTP ${res.status}: ${text}`);
      }

      setResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ padding: 40, fontFamily: "system-ui, sans-serif", maxWidth: 800 }}>
      <h1>Freedom Constraint Engine</h1>
      <p style={{ color: "#666" }}>Pre-decision validity gate — SPEC-FCE-001</p>

      <div style={{ marginBottom: 20 }}>
        <label style={{ marginRight: 10 }}>Domain:</label>
        <select value={domain} onChange={e => setDomain(e.target.value)}>
          <option value="finance_v1">finance_v1</option>
          <option value="health_v1">health_v1</option>
          <option value="career_v1">career_v1</option>
        </select>
      </div>

      <button
        onClick={handleEvaluate}
        disabled={loading}
        style={{ padding: "10px 24px", cursor: loading ? "not-allowed" : "pointer" }}
      >
        {loading ? "Evaluating..." : "Evaluate"}
      </button>

      {error && (
        <div style={{ marginTop: 20, padding: 20, background: "#fee", color: "#c00", borderRadius: 6 }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 20 }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
            <div style={{ background: "#f0f9ff", padding: 16, borderRadius: 6 }}>
              <strong>Confidence Score</strong>
              <div style={{ fontSize: 32, fontWeight: "bold", color: "#0066cc" }}>
                {(result.confidence_score * 100).toFixed(1)}%
              </div>
            </div>
            <div style={{ background: "#f0fdf4", padding: 16, borderRadius: 6 }}>
              <strong>Allowed Actions</strong>
              <div>{result.allowed_actions?.length ?? 0} actions</div>
              <strong style={{ marginTop: 8, display: "block" }}>Blocked Actions</strong>
              <div>{result.blocked_actions?.length ?? 0} actions</div>
            </div>
          </div>
          <pre style={{ background: "#f4f4f4", padding: 20, borderRadius: 6, overflow: "auto", fontSize: 13 }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </main>
  );
}
