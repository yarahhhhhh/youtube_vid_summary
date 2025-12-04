import { useState } from "react";
import "./App.css";
import.meta.env.VITE_API_URL


function App() {
  const [videoID, setID] = useState("");
  const [summary, setSummary] = useState("");
  const [language, setLanguage] = useState("en");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function HandleSubmit() {
    setLoading(true);
    setError("");
    setSummary("");


    const url = `${import.meta.env.VITE_API_URL}/generate_summary`;


    const request = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: videoID, lang: language })
    });

    const data = await request.json();

    if (data.error) {
      setError(data.error);
      setLoading(false);
      return;
    }

    setSummary(data.summary);
    setLoading(false);
  }

  return (
    <div className="app-container">
      <h2
        className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600"
        style={{ fontFamily: "monospace", letterSpacing: "0.1em" }}
      >
        VIDEO SUMMARIZER
      </h2>

      <div className="top-inputs">
        <input value={videoID} onChange={(e) => setID(e.target.value)} />
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="en">English</option>
          <option value="fr">French</option>
        </select>

        <button onClick={HandleSubmit}>Click me</button>
      </div>

      <div className="summary-box">
        {loading && <div>Studying the video 🤖</div>}
        {!loading && error && <p>{error}</p>}
        {!loading && !error && summary && <p>{summary}</p>}
      </div>

      <p
        className="text-center text-slate-700"
        style={{ fontFamily: "monospace", fontSize: "0.75rem" }}
      >
        / POWERED BY ADVANCED AI SYSTEMS /
      </p>
    </div>
  );
}

export default App;
