import React, { useState, useRef, useEffect } from "react";
import { UploadCloud, File, AlertCircle } from "lucide-react";
import API from "../services/api";

const HEALTH_FACTS = [
  "Eating a colorful variety of fruits and vegetables ensures you get a wide range of essential vitamins and minerals.",
  "Regular cardiovascular exercise increases blood flow, which helps support brain health and cognitive function.",
  "Staying well-hydrated helps your body flush toxins, maintain skin elasticity, and keep your joints lubricated.",
  "An adult human skeleton is made up of 206 bones, whereas infants are born with around 270 bones.",
  "Your heart beats about 100,000 times a day, pumping around 2,000 gallons (7,570 liters) of blood throughout your body.",
  "Getting 7-9 hours of quality sleep each night is essential for muscle recovery, memory consolidation, and hormone balance.",
];

interface UploadProps {
  file: File | null;
  setFile: (file: File | null) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
  onUploadSuccess: (data: any) => void;
}

const Upload: React.FC<UploadProps> = ({ file, setFile, loading, setLoading, onUploadSuccess }) => {
  const [dragActive, setDragActive] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [factIndex, setFactIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Rotating facts carousel effect when loading is active
  useEffect(() => {
    let interval: any;
    if (loading) {
      interval = setInterval(() => {
        setFactIndex((prev) => (prev + 1) % HEALTH_FACTS.length);
      }, 4000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [loading]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const validateFile = (selectedFile: File): boolean => {
    const allowedTypes = ["application/pdf", "image/jpeg", "image/png", "image/jpg"];
    if (!allowedTypes.includes(selectedFile.type)) {
      setErrorMessage("Only PDF, JPG, JPEG, and PNG files are allowed.");
      return false;
    }
    setErrorMessage("");
    return true;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFile(droppedFile)) {
        setFile(droppedFile);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
      }
    }
  };

  const triggerInputClick = () => {
    inputRef.current?.click();
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setErrorMessage("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      // Backend expects the form field "question" as well
      formData.append("question", "Explain my report");

      const response = await API.post("/medical/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      onUploadSuccess(response.data);
    } catch (error: any) {
      console.error("Upload error:", error);
      setErrorMessage(
        error.response?.data?.detail || 
        error.message || 
        "Failed to analyze the medical report. Please check if the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="card loader-wrapper">
        <div className="spinner"></div>
        <div className="loading-text">Analyzing Your Medical Report...</div>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginBottom: "2rem" }}>
          Our AI medical agents are extracting clinical data, analyzing laboratory values, and cross-referencing health history.
        </p>
        
        <div className="facts-carousel">
          <div className="fact-title">Did You Know?</div>
          <div className="fact-content">{HEALTH_FACTS[factIndex]}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="card" style={{ maxWidth: "650px", margin: "0 auto", width: "100%" }}>
      <div className="card-header">
        <h2 className="card-title">
          <UploadCloud size={20} />
          Upload Health Report
        </h2>
      </div>

      <div
        className={`upload-zone ${dragActive ? "drag-active" : ""}`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={triggerInputClick}
      >
        <input
          ref={inputRef}
          type="file"
          className="file-input"
          onChange={handleFileChange}
          accept=".pdf, image/jpeg, image/png, image/jpg"
        />
        
        <div className="upload-icon-wrapper">
          <UploadCloud size={32} />
        </div>
        
        <div className="upload-title">Drag & drop your medical file</div>
        <div className="upload-desc">
          Supports medical report sheets, blood tests, clinical scans, or prescription notes (PDF, JPG, JPEG, PNG).
        </div>
        <button type="button" className="btn btn-secondary">Select File</button>
      </div>

      {errorMessage && (
        <div style={{
          display: "flex", 
          alignItems: "center", 
          gap: "0.5rem", 
          color: "var(--danger)", 
          fontSize: "0.875rem", 
          marginTop: "1rem",
          justifyContent: "center"
        }}>
          <AlertCircle size={16} />
          <span>{errorMessage}</span>
        </div>
      )}

      {file && (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginTop: "1.5rem" }}>
          <div className="file-preview">
            <div className="file-info">
              <File size={24} style={{ color: "var(--primary)" }} />
              <div className="file-details">
                <span className="file-name">{file.name}</span>
                <span className="file-size">{formatBytes(file.size)}</span>
              </div>
            </div>
            <button className="btn btn-ghost" onClick={(e) => { e.stopPropagation(); setFile(null); }} style={{ padding: "0.25rem" }}>
              ✕
            </button>
          </div>
          
          <button 
            className="btn btn-primary" 
            onClick={handleUpload}
            style={{ marginTop: "1.5rem", paddingLeft: "2.5rem", paddingRight: "2.5rem" }}
          >
            Start AI Diagnosis
          </button>
        </div>
      )}
    </div>
  );
};

export default Upload;