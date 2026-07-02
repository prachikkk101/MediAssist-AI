import React, { useState, useRef, useEffect } from "react";
import { Send, Bot, User } from "lucide-react";
import API from "../services/api";

interface Message {
  sender: "user" | "assistant";
  text: string;
  timestamp: Date;
}

interface ChatProps {
  file: File | null;
}

const QUICK_QUESTIONS = [
  "Are there any values out of the normal range?",
  "Explain this in simple terms.",
  "What questions should I ask my doctor?",
  "What dietary suggestions are recommended?"
];

const Chat: React.FC<ChatProps> = ({ file }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "assistant",
      text: "Hello! I am your Medical AI Assistant. Ask me any follow-up questions about your health report.",
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState("");
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const sendMessage = async (textToSend: string) => {
    if (!textToSend.trim() || !file || sending) return;

    // Add user message
    const userMsg: Message = {
      sender: "user",
      text: textToSend,
      timestamp: new Date()
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputText("");
    setSending(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("question", textToSend);

      const response = await API.post("/medical/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      // Add AI reply
      const botMsg: Message = {
        sender: "assistant",
        text: response.data.answer || "I've analyzed your question relative to the report details, but couldn't construct a proper response. Please try again.",
        timestamp: new Date()
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (error: any) {
      console.error("Chat error:", error);
      const errorMsg: Message = {
        sender: "assistant",
        text: "Error: Failed to fetch a reply. Please ensure your backend server is running and reachable.",
        timestamp: new Date()
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      sendMessage(inputText);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-wrapper">
      <div className="chat-header">
        <Bot size={24} style={{ color: "var(--primary)" }} />
        <div className="chat-title-group">
          <span className="chat-title">Medical Assistant AI</span>
          <span className="chat-subtitle">Ask questions about your report</span>
        </div>
      </div>

      <div className="chat-messages-area">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-message-row ${msg.sender}`}>
            <div className="chat-bubble">
              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", marginBottom: "0.25rem" }}>
                {msg.sender === "assistant" ? (
                  <Bot size={14} style={{ color: "var(--primary)" }} />
                ) : (
                  <User size={14} style={{ color: "var(--accent)" }} />
                )}
                <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-secondary)" }}>
                  {msg.sender === "assistant" ? "Medical AI" : "You"}
                </span>
              </div>
              <p style={{ margin: 0, fontSize: "0.9rem", whiteSpace: "pre-wrap" }}>{msg.text}</p>
              <span className="message-time">{formatTime(msg.timestamp)}</span>
            </div>
          </div>
        ))}
        {sending && (
          <div className="chat-message-row assistant">
            <div className="chat-bubble">
              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", marginBottom: "0.25rem" }}>
                <Bot size={14} style={{ color: "var(--primary)" }} />
                <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-secondary)" }}>Medical AI</span>
              </div>
              <div className="chat-typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-quick-replies">
        {QUICK_QUESTIONS.map((q, idx) => (
          <button
            key={idx}
            className="quick-reply-btn"
            onClick={() => sendMessage(q)}
            disabled={sending || !file}
          >
            {q}
          </button>
        ))}
      </div>

      <div className="chat-input-container">
        <input
          type="text"
          className="chat-input"
          placeholder={file ? "Ask about laboratory levels, medication guidance..." : "Please upload a report first"}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={sending || !file}
        />
        <button
          className="btn btn-primary"
          onClick={() => sendMessage(inputText)}
          disabled={sending || !inputText.trim() || !file}
          style={{ padding: "0.6rem" }}
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
};

export default Chat;
