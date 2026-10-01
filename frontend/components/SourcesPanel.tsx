"use client";

import React from "react";
import { Claim } from "../lib/api";

interface SourcesPanelProps {
  claims: Claim[];
  isOpen: boolean;
  onClose: () => void;
}

export function SourcesPanel({ claims, isOpen, onClose }: SourcesPanelProps) {
  if (!isOpen) return null;

  return (
    <aside className="sources-panel">
      <div className="sources-header">
        <h2>
          <span>📚</span>
          Sources & Citations
        </h2>
        <button
          onClick={onClose}
          style={{
            background: "transparent",
            border: "none",
            color: "var(--text-muted)",
            fontSize: "1.25rem",
            cursor: "pointer",
          }}
          aria-label="Close sources panel"
        >
          ✕
        </button>
      </div>

      <div className="sources-content">
        <div className="m1-notice-box">
          <h3>🔬 Milestone 1 Architecture Notice</h3>
          <p>
            In <strong>Milestone 1</strong>, answers and factual claims are generated strictly from the LLM&apos;s
            internal knowledge (parametric memory). All citation sources are intentionally set to{" "}
            <code>null</code>.
          </p>
          <p style={{ marginTop: "0.5rem" }}>
            <strong>Milestone 2</strong> will slide a retrieval-augmented generation (RAG) layer underneath, linking
            each claim directly to verified sources such as USDA FoodData Central and peer-reviewed journals.
          </p>
        </div>

        <div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "0.75rem",
            }}
          >
            <span
              style={{
                fontSize: "0.75rem",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                color: "var(--text-muted)",
              }}
            >
              Extracted Claims ({claims.length})
            </span>
          </div>

          {claims.length === 0 ? (
            <div
              style={{
                padding: "2rem 1rem",
                textAlign: "center",
                color: "var(--text-muted)",
                fontSize: "0.85rem",
                border: "1px dashed var(--border-subtle)",
                borderRadius: "var(--radius-md)",
              }}
            >
              No claims extracted in this conversation yet. Ask a nutrition question to see claims appear here.
            </div>
          ) : (
            <div className="sources-list">
              {claims.map((claim, idx) => (
                <div
                  key={claim.id || idx}
                  style={{
                    padding: "0.85rem",
                    borderRadius: "var(--radius-md)",
                    background: "rgba(255, 255, 255, 0.03)",
                    border: "1px solid var(--border-subtle)",
                    display: "flex",
                    flexDirection: "column",
                    gap: "0.4rem",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <span
                      style={{
                        fontSize: "0.7rem",
                        fontWeight: 700,
                        color: "var(--primary-400)",
                        background: "rgba(16, 185, 129, 0.12)",
                        padding: "2px 6px",
                        borderRadius: "4px",
                      }}
                    >
                      Claim #{idx + 1}
                    </span>
                    <span
                      style={{
                        fontSize: "0.65rem",
                        color: "var(--accent-amber)",
                        marginLeft: "auto",
                      }}
                    >
                      ● Source: null (M1)
                    </span>
                  </div>

                  <p style={{ fontSize: "0.825rem", color: "var(--text-primary)", lineHeight: 1.5 }}>
                    {claim.text}
                  </p>

                  <div
                    style={{
                      fontSize: "0.7rem",
                      color: "var(--text-muted)",
                      paddingTop: "0.25rem",
                      borderTop: "1px solid rgba(255, 255, 255, 0.04)",
                    }}
                  >
                    Target verification dataset: <em>USDA FoodData Central / FDA (Milestone 2)</em>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
