"use client";

import React from "react";

interface HeaderProps {
  activeTitle?: string;
  sourcesCount: number;
  isSourcesOpen: boolean;
  onToggleSources: () => void;
  onToggleSidebar: () => void;
  backendOnline: boolean;
}

export function Header({
  activeTitle = "Nutritional Inquiry Workspace",
  sourcesCount,
  isSourcesOpen,
  onToggleSources,
  onToggleSidebar,
  backendOnline,
}: HeaderProps) {
  return (
    <header className="top-header">
      <div className="header-left">
        <button
          onClick={onToggleSidebar}
          className="toggle-sidebar-btn"
          aria-label="Toggle Navigation"
          title="Toggle Consultations Sidebar"
        >
          <span className="material-symbols-outlined">menu</span>
        </button>

        <div className="memory-active-pill">
          <span className="pulse-dot" />
          <span>Parametric Memory: Active</span>
        </div>

        <div style={{ width: 1, height: 16, background: "var(--outline-variant)" }} />

        <span className="header-title-text" title={activeTitle}>
          {activeTitle}
        </span>
      </div>

      <div className="header-right">
        <button
          onClick={onToggleSources}
          className={`citations-btn ${isSourcesOpen ? "active" : ""}`}
          title="Inspect extracted claims & citation grounding"
        >
          <span className="material-symbols-outlined" style={{ fontSize: 18, color: "var(--primary)" }}>
            library_books
          </span>
          <span>{sourcesCount} Citations Active</span>
        </button>

        <div
          style={{
            width: 34,
            height: 34,
            borderRadius: "50%",
            background: "var(--primary)",
            color: "var(--on-primary)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
          title={backendOnline ? "Gemini 3.1 Flash Online" : "Local Mode"}
        >
          <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
            psychology
          </span>
        </div>
      </div>
    </header>
  );
}
