import { useState } from "react";
import { Activity, ShieldAlert, Heart, ClipboardCheck, MessageSquare, Pill } from "lucide-react";
import Upload from "./components/Upload";
import Dashboard from "./components/Dashboard";
import Chat from "./components/Chat";

interface AnalysisResult {
  filename: string;
  extracted_text: string;
  answer: string;
  summary: string;
  nutrition: string;
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const handleUploadSuccess = (data: any) => {
    setAnalysisResult({
      filename: data.filename || file?.name || "Report.pdf",
      extracted_text: data.extracted_text || "",
      answer: data.answer || "",
      summary: data.summary || "",
      nutrition: data.nutrition || "",
    });
  };

  const handleReset = () => {
    setFile(null);
    setAnalysisResult(null);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo-container">
          <div className="logo-icon">
            <Activity size={24} />
          </div>
          <span className="app-title">Medical AI Analyzer</span>
        </div>
        <div className="badge-demo">
          {analysisResult ? "Report Loaded" : "Diagnostic Portal"}
        </div>
      </header>

      <main className="main-content">
        {!analysisResult ? (
          <div className="welcome-container">
            <h1 className="welcome-title">
              Understand Your Medical Reports in Seconds
            </h1>
            <p className="welcome-subtitle">
              Upload laboratory values, blood tests, or diagnostic scans. Our specialized AI clinical agents extract key details and explain medical findings in simple terms.
            </p>

            <div className="features-grid">
              <div className="feature-box">
                <div className="feature-icon-wrapper">
                  <ClipboardCheck size={20} />
                </div>
                <h3 className="feature-title">Clinical Summaries</h3>
                <p className="feature-desc">
                  Extracts complex diagnostic numbers and translates findings into clear, structured takeaways.
                </p>
              </div>

              <div className="feature-box">
                <div className="feature-icon-wrapper">
                  <MessageSquare size={20} />
                </div>
                <h3 className="feature-title">Follow-up Chat</h3>
                <p className="feature-desc">
                  Ask immediate questions about markers, ranges, and clinical recommendations.
                </p>
              </div>

              <div className="feature-box">
                <div className="feature-icon-wrapper">
                  <Pill size={20} />
                </div>
                <h3 className="feature-title">Nutrition & Lifestyle</h3>
                <p className="feature-desc">
                  Receive personalized meal plans and lifestyle habits tailored to your medical findings.
                </p>
              </div>

              <div className="feature-box">
                <div className="feature-icon-wrapper">
                  <Heart size={20} />
                </div>
                <h3 className="feature-title">100% Confidential</h3>
                <p className="feature-desc">
                  Files are processed securely. Your data is never sold or used for training models.
                </p>
              </div>
            </div>

            <Upload
              file={file}
              setFile={setFile}
              loading={loading}
              setLoading={setLoading}
              onUploadSuccess={handleUploadSuccess}
            />
          </div>
        ) : (
          <div className="grid-dashboard">
            <Dashboard result={analysisResult} onReset={handleReset} />
            <Chat file={file} />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem", marginBottom: "1rem", color: "var(--text-secondary)" }}>
          <ShieldAlert size={16} style={{ color: "var(--warning)" }} />
          <span style={{ fontWeight: 600 }}>Medical AI Disclaimer</span>
        </div>
        <p style={{ maxWidth: "800px", margin: "0 auto", lineHeight: 1.5 }}>
          This application utilizes advanced language models and artificial intelligence agents to analyze health records. It is intended solely for educational and reference purposes. It does not provide medical diagnoses, treatment suggestions, or official clinical prescriptions. Always consult a qualified physician or healthcare provider regarding any questions or clinical concerns.
        </p>
        <div style={{ marginTop: "1.5rem" }}>
          &copy; {new Date().getFullYear()} Medical AI Inc. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

export default App;