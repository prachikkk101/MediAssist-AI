import React, { useState, useRef, useEffect } from "react";
import { UploadCloud, File as FileIcon, AlertCircle } from "lucide-react";
import { analyzeReportWithPolling } from "../services/api";

const HEALTH_FACTS = [
  "Eating a colorful variety of fruits and vegetables provides essential vitamins and minerals.",
  "Regular cardiovascular exercise supports brain and heart health.",
  "Staying hydrated helps maintain normal body functions.",
  "An adult human skeleton typically has 206 bones.",
  "Your heart beats around 100,000 times a day.",
  "Most adults benefit from 7–9 hours of sleep each night.",
];

interface UploadProps {
  file: File | null;
  setFile: (file: File | null) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
  onUploadSuccess: (data: any) => void;
}

const Upload: React.FC<UploadProps> = ({
  file,
  setFile,
  loading,
  setLoading,
  onUploadSuccess,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [factIndex, setFactIndex] = useState(0);
  const [jobStatus, setJobStatus] = useState("");

  const inputRef = useRef<HTMLInputElement>(null);

  // Rotate health facts while the report is processing.
  useEffect(() => {
    if (!loading) return;

    const interval = window.setInterval(() => {
      setFactIndex((prev) => (prev + 1) % HEALTH_FACTS.length);
    }, 4000);

    return () => window.clearInterval(interval);
  }, [loading]);

  const validateFile = (selectedFile: File): boolean => {
    const allowedTypes = [
      "application/pdf",
      "image/jpeg",
      "image/png",
    ];

    const allowedExtensions = /\.(pdf|jpe?g|png)$/i;

    if (
      !allowedTypes.includes(selectedFile.type) &&
      !allowedExtensions.test(selectedFile.name)
    ) {
      setErrorMessage(
        "Only PDF, JPG, JPEG, and PNG files are allowed."
      );
      return false;
    }

    if (selectedFile.size === 0) {
      setErrorMessage("The selected file is empty.");
      return false;
    }

    setErrorMessage("");
    return true;
  };

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();

    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFile = e.dataTransfer.files?.[0];

    if (droppedFile && validateFile(droppedFile)) {
      setFile(droppedFile);
    }
  };

  const handleFileChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const selectedFile = e.target.files?.[0];

    if (selectedFile && validateFile(selectedFile)) {
      setFile(selectedFile);
    }

    // Allow selecting the same file again.
    e.target.value = "";
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";

    const units = ["Bytes", "KB", "MB", "GB"];
    const index = Math.min(
      Math.floor(Math.log(bytes) / Math.log(1024)),
      units.length - 1
    );

    return `${parseFloat(
      (bytes / Math.pow(1024, index)).toFixed(2)
    )} ${units[index]}`;
  };

  const handleUpload = async () => {
    if (!file || loading) return;

    setLoading(true);
    setErrorMessage("");
    setJobStatus("queued");

    try {
      console.log("Uploading medical report:", {
        fileName: file.name,
        fileSize: file.size,
        fileType: file.type,
      });

      // Starts a background job and polls until the analysis is done.
      const result = await analyzeReportWithPolling(
        file,
        "Explain my report",
        setJobStatus
      );

      console.log("Analysis result:", result);

      onUploadSuccess(result);
    } catch (error: any) {
      console.error("Medical report upload failed:", error);

      if (error.response) {
        // The server responded with an HTTP error.
        console.error("HTTP status:", error.response.status);
        console.error("Server response:", error.response.data);

        const detail = error.response.data?.detail;
        const message =
          typeof detail === "string"
            ? detail
            : error.response.status === 404
            ? "Upload endpoint not found. Check the backend route."
            : error.response.status === 422
            ? "The uploaded form fields do not match the backend endpoint."
            : `Server error (${error.response.status}). Check the backend terminal.`;

        setErrorMessage(message);
      } else if (error.request) {
        // A request was made, but no readable response was received.
        console.error("Request URL:", error.config?.baseURL);
        console.error("Request path:", error.config?.url);
        console.error("Network details:", error.message);

        setErrorMessage(
          "Cannot reach the API or read its response. Check that the backend is running, the API URL is correct, and CORS allows this frontend origin."
        );
      } else {
        setErrorMessage(
          error.message || "Unable to start the upload."
        );
      }
    } finally {
      setLoading(false);
      setJobStatus("");
    }
  };

  if (loading) {
    return (
      <div className="card loader-wrapper">
        <div className="spinner" />
        <div className="loading-text">
          Analyzing Your Medical Report...
        </div>

        <p
          style={{
            color: "var(--text-secondary)",
            fontSize: "0.9rem",
            marginBottom: "0.5rem",
          }}
        >
          Our AI agents are extracting clinical data and
          analyzing your report. Processing may take a few minutes.
        </p>

        {jobStatus && (
          <p
            style={{
              color: "var(--text-secondary)",
              fontSize: "0.8rem",
              marginBottom: "1.5rem",
            }}
          >
            Status:{" "}
            {jobStatus === "queued"
              ? "waiting to start"
              : jobStatus === "running"
              ? "analyzing"
              : jobStatus}
          </p>
        )}

        <div className="facts-carousel">
          <div className="fact-title">Did You Know?</div>
          <div className="fact-content">
            {HEALTH_FACTS[factIndex]}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className="card"
      style={{
        maxWidth: "650px",
        margin: "0 auto",
        width: "100%",
      }}
    >
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
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          className="file-input"
          accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
          onChange={handleFileChange}
        />

        <div className="upload-icon-wrapper">
          <UploadCloud size={32} />
        </div>

        <div className="upload-title">
          Drag &amp; drop your medical file
        </div>

        <div className="upload-desc">
          Supports medical reports, blood tests, clinical scans,
          and prescription notes (PDF, JPG, JPEG, PNG).
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={(e) => {
            e.stopPropagation();
            inputRef.current?.click();
          }}
        >
          Select File
        </button>
      </div>

      {errorMessage && (
        <div
          role="alert"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
            color: "var(--danger)",
            fontSize: "0.875rem",
            marginTop: "1rem",
            justifyContent: "center",
            overflowWrap: "anywhere",
          }}
        >
          <AlertCircle size={16} />
          <span>{errorMessage}</span>
        </div>
      )}

      {file && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            marginTop: "1.5rem",
          }}
        >
          <div className="file-preview">
            <div className="file-info">
              <FileIcon
                size={24}
                style={{ color: "var(--primary)" }}
              />

              <div className="file-details">
                <span className="file-name">{file.name}</span>
                <span className="file-size">
                  {formatBytes(file.size)}
                </span>
              </div>
            </div>

            <button
              type="button"
              className="btn btn-ghost"
              aria-label="Remove selected file"
              onClick={() => {
                setFile(null);
                setErrorMessage("");
              }}
              style={{ padding: "0.25rem" }}
            >
              ✕
            </button>
          </div>

          <button
            type="button"
            className="btn btn-primary"
            onClick={handleUpload}
            style={{
              marginTop: "1.5rem",
              paddingLeft: "2.5rem",
              paddingRight: "2.5rem",
            }}
          >
            Start AI Diagnosis
          </button>
        </div>
      )}
    </div>
  );
};

export default Upload;