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
    <aside className="sources-drawer">
      <div className="drawer-header">
        <h3>
          <span className="material-symbols-outlined" style={{ color: "var(--primary)" }}>
            library_books
          </span>
          Evidence & Citations
        </h3>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span
            style={{
              padding: "2px 8px",
              borderRadius: "9999px",
              background: "var(--secondary-container)",
              color: "var(--on-secondary-container)",
              fontSize: "0.75rem",
              fontWeight: 600,
            }}
          >
            {claims.length} Claims
          </span>
          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              color: "var(--outline)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              padding: 4,
            }}
            aria-label="Close citations drawer"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
      </div>

      <div className="drawer-body">
        <div className="m1-grounding-notice">
          <h4>🔬 Milestone 1 Grounding Notice</h4>
          <p>
            In <strong>Milestone 1</strong>, answers and factual claims are generated entirely from the LLM&apos;s
            internal knowledge (parametric memory). Citation sources are strictly initialized to <code>null</code>.
          </p>
          <p style={{ marginTop: "0.5rem" }}>
            <strong>Milestone 2</strong> will connect a RAG retrieval pipeline (indexing USDA FoodData Central and FDA
            standards) to turn these into clickable, verified citations.
          </p>
        </div>

        <div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "0.75rem",
              fontSize: "0.75rem",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              color: "var(--outline)",
            }}
          >
            <span>Extracted Claims Dossier</span>
          </div>

          {claims.length === 0 ? (
            <div
              style={{
                padding: "2rem 1rem",
                textAlign: "center",
                color: "var(--outline)",
                fontSize: "0.85rem",
                border: "1px dashed rgba(116, 120, 113, 0.2)",
                borderRadius: "var(--radius-md)",
              }}
            >
              No factual claims extracted yet. Send a question to see claims appear here.
            </div>
          ) : (
            <div className="citations-dossier-list">
              {claims.map((claim, idx) => (
                <div key={claim.id || idx} className="citation-card-entry">
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <span
                      style={{
                        fontSize: "0.7rem",
                        fontWeight: 700,
                        textTransform: "uppercase",
                        letterSpacing: "0.05em",
                        color: "var(--secondary)",
                      }}
                    >
                      Extracted Claim [{idx + 1}]
                    </span>
                    <span
                      style={{
                        fontSize: "0.65rem",
                        fontWeight: 600,
                        color: "var(--tertiary)",
                        background: "var(--surface-container-high)",
                        padding: "2px 6px",
                        borderRadius: "9999px",
                      }}
                    >
                      ● Source: null (M1)
                    </span>
                  </div>

                  <p style={{ fontSize: "0.85rem", color: "var(--on-surface)", lineHeight: 1.5, margin: "0.25rem 0" }}>
                    {claim.text}
                  </p>

                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      fontSize: "0.7rem",
                      color: "var(--outline)",
                      paddingTop: "0.35rem",
                      borderTop: "1px solid rgba(116, 120, 113, 0.08)",
                    }}
                  >
                    <span>Target: USDA FoodData Central</span>
                    <span style={{ color: "var(--primary)", fontWeight: 600 }}>Milestone 2 Seam</span>
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
