import React, { useState } from "react";
import { FileText, Leaf, BookOpen, FileCode2, RefreshCw } from "lucide-react";

interface AnalysisResult {
  filename: string;
  extracted_text: string;
  answer: string;
  summary: string;
  nutrition: string;
}

interface DashboardProps {
  result: AnalysisResult;
  onReset: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ result, onReset }) => {
  const [activeTab, setActiveTab] = useState<"summary" | "explain" | "nutrition" | "raw">("summary");

  // Inline custom formatter to safely parse markdown headings, lists, bold text and spacing
  const renderFormattedText = (text: string) => {
    if (!text) return <p>No data provided by the analysis agent.</p>;
    
    const lines = text.split("\n");
    let inList = false;
    let listType: "ul" | "ol" | null = null;
    const elements: React.ReactNode[] = [];

    const parseBold = (str: string) => {
      const parts = str.split("**");
      return parts.map((part, idx) => {
        if (idx % 2 === 1) {
          return <strong key={idx}>{part}</strong>;
        }
        return part;
      });
    };

    lines.forEach((line, idx) => {
      const trimmed = line.trim();
      
      // Headers
      if (trimmed.startsWith("### ")) {
        closeList();
        elements.push(<h4 key={`h4-${idx}`} style={{ marginTop: "1rem", marginBottom: "0.5rem", color: "var(--text-primary)" }}>{parseBold(trimmed.substring(4))}</h4>);
        return;
      }
      if (trimmed.startsWith("## ")) {
        closeList();
        elements.push(<h3 key={`h3-${idx}`} style={{ marginTop: "1.25rem", marginBottom: "0.5rem", color: "var(--text-primary)", fontSize: "1.15rem" }}>{parseBold(trimmed.substring(3))}</h3>);
        return;
      }
      if (trimmed.startsWith("# ")) {
        closeList();
        elements.push(<h2 key={`h2-${idx}`} style={{ marginTop: "1.5rem", marginBottom: "0.75rem", color: "var(--text-primary)", fontSize: "1.3rem" }}>{parseBold(trimmed.substring(2))}</h2>);
        return;
      }

      // Unordered lists
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        if (!inList || listType !== "ul") {
          closeList();
          inList = true;
          listType = "ul";
        }
        const bulletText = trimmed.replace(/^[\s*-]+/, "");
        elements.push(<li key={`li-ul-${idx}`} style={{ marginLeft: "1.5rem", marginBottom: "0.25rem", listStyleType: "disc" }}>{parseBold(bulletText)}</li>);
        return;
      }

      // Ordered lists
      const orderedMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
      if (orderedMatch) {
        if (!inList || listType !== "ol") {
          closeList();
          inList = true;
          listType = "ol";
        }
        const itemText = orderedMatch[2];
        elements.push(<li key={`li-ol-${idx}`} style={{ marginLeft: "1.5rem", marginBottom: "0.25rem", listStyleType: "decimal" }}>{parseBold(itemText)}</li>);
        return;
      }

      // Empty line
      if (trimmed === "") {
        closeList();
        elements.push(<div key={`space-${idx}`} style={{ height: "0.5rem" }} />);
        return;
      }

      // Regular paragraph
      closeList();
      elements.push(<p key={`p-${idx}`} style={{ marginBottom: "0.75rem", lineHeight: "1.6" }}>{parseBold(trimmed)}</p>);
    });

    function closeList() {
      if (inList) {
        inList = false;
        listType = null;
      }
    }

    return <div className="markdown-output">{elements}</div>;
  };

  return (
    <div className="card">
      <div className="dashboard-header-bar">
        <div className="report-meta-info">
          <FileText size={20} className="logo-icon" style={{ padding: "0.25rem" }} />
          <div>
            <span style={{ fontSize: "0.75rem", textTransform: "uppercase", fontWeight: 700, color: "var(--text-tertiary)" }}>Analyzed Report</span>
            <div className="file-name" style={{ fontSize: "1rem", fontWeight: 600 }}>{result.filename || "Medical Report"}</div>
          </div>
        </div>
        <button className="btn btn-secondary" onClick={onReset}>
          <RefreshCw size={16} />
          Analyze New
        </button>
      </div>

      <nav className="tabs-navigation">
        <button
          className={`tab-btn ${activeTab === "summary" ? "active" : ""}`}
          onClick={() => setActiveTab("summary")}
        >
          <FileText size={16} />
          Summary
        </button>
        <button
          className={`tab-btn ${activeTab === "explain" ? "active" : ""}`}
          onClick={() => setActiveTab("explain")}
        >
          <BookOpen size={16} />
          Explanation
        </button>
        <button
          className={`tab-btn ${activeTab === "nutrition" ? "active" : ""}`}
          onClick={() => setActiveTab("nutrition")}
        >
          <Leaf size={16} />
          Nutrition & Diet
        </button>
        <button
          className={`tab-btn ${activeTab === "raw" ? "active" : ""}`}
          onClick={() => setActiveTab("raw")}
        >
          <FileCode2 size={16} />
          Raw Text
        </button>
      </nav>

      <div className="tab-content">
        {activeTab === "summary" && (
          <div className="tab-pane">
            <h3 style={{ fontFamily: "var(--font-display)", fontSize: "1.1rem", marginBottom: "1rem" }}>Report Summary</h3>
            {renderFormattedText(result.summary)}
          </div>
        )}

        {activeTab === "explain" && (
          <div className="tab-pane">
            <h3 style={{ fontFamily: "var(--font-display)", fontSize: "1.1rem", marginBottom: "1rem" }}>Medical Insight & Findings</h3>
            {renderFormattedText(result.answer)}
          </div>
        )}

        {activeTab === "nutrition" && (
          <div className="tab-pane">
            <h3 style={{ fontFamily: "var(--font-display)", fontSize: "1.1rem", marginBottom: "1rem" }}>Dietary & Nutrition Recommendations</h3>
            {renderFormattedText(result.nutrition)}
          </div>
        )}

        {activeTab === "raw" && (
          <div className="tab-pane">
            <h3 style={{ fontFamily: "var(--font-display)", fontSize: "1.1rem", marginBottom: "1rem" }}>Extracted Report Text</h3>
            <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "0.75rem" }}>
              Below is the first 500 characters of text extracted from your uploaded report:
            </p>
            <div className="extracted-raw-section">
              {result.extracted_text || "No readable text extracted."}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
