"use client";

import React from "react";

interface HeaderProps {
  sourcesCount: number;
  isSourcesOpen: boolean;
  onToggleSources: () => void;
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
  backendOnline: boolean;
}

export function Header({
  sourcesCount,
  isSourcesOpen,
  onToggleSources,
  onToggleSidebar,
  backendOnline,
}: HeaderProps) {
  return (
    <header className="chat-header">
      <div className="header-brand">
        <button
          onClick={onToggleSidebar}
          aria-label="Toggle Conversations"
          style={{
            background: "transparent",
            border: "none",
            color: "var(--text-secondary)",
            cursor: "pointer",
            fontSize: "1.2rem",
            display: "flex",
            alignItems: "center",
          }}
        >
          ☰
        </button>

        <div className="brand-icon">🥗</div>
        <div className="brand-info">
          <h1>
            NutriBot
            <span className="badge-m1">Milestone 1</span>
          </h1>
          <p>
            {backendOnline ? (
              <span style={{ color: "#34d399", display: "inline-flex", alignItems: "center", gap: 4 }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#34d399" }} />
                Gemini 3.1 Flash • Structured Output
              </span>
            ) : (
              <span style={{ color: "#f87171" }}>Offline mode</span>
            )}
          </p>
        </div>
      </div>

      <div className="header-actions">
        <button
          onClick={onToggleSources}
          className={`sources-toggle-btn ${isSourcesOpen ? "active" : ""}`}
          title="View factual claims & citation status"
        >
          <span style={{ fontSize: "0.9rem" }}>📚</span>
          Sources ({sourcesCount})
        </button>
      </div>
    </header>
  );
}
