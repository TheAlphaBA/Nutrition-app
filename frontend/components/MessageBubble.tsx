"use client";

import React, { useState } from "react";
import { Message, Claim } from "../lib/api";

interface MessageBubbleProps {
  message: Message;
  onInspectClaim?: (claim: Claim) => void;
}

export function MessageBubble({ message, onInspectClaim }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const hasClaims = message.claims && message.claims.length > 0;
  const isGuardrailBlocked = message.guardrail_triggered;
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const renderFormattedText = (text: string) => {
    const lines = text.split("\n");
    return lines.map((line, idx) => {
      const trimmed = line.trim();
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        const bulletText = trimmed.substring(2);
        return (
          <li key={idx} style={{ marginLeft: "1.25rem", marginBottom: "0.35rem" }}>
            {formatSpans(bulletText)}
          </li>
        );
      }
      if (trimmed === "") {
        return <div key={idx} style={{ height: "0.5rem" }} />;
      }
      return (
        <p key={idx} style={{ marginBottom: "0.55rem" }}>
          {formatSpans(line)}
        </p>
      );
    });
  };

  const formatSpans = (str: string) => {
    const parts = str.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={i} style={{ color: "var(--on-surface)", fontWeight: 600 }}>
            {part.slice(2, -2)}
          </strong>
        );
      }
      return part;
    });
  };

  if (isUser) {
    return (
      <div className="user-message-row">
        <div className="user-pebble">
          <div className="user-pebble-header">
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div
                style={{
                  width: 20,
                  height: 20,
                  borderRadius: "50%",
                  background: "var(--surface-container-highest)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "var(--outline)",
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 13 }}>
                  person
                </span>
              </div>
              <span>Dietary Inquiry</span>
            </div>
            <span>User</span>
          </div>

          <p className="user-pebble-body">{message.content}</p>
        </div>
      </div>
    );
  }

  // Assistant Message Card
  return (
    <article className="assistant-card">
      <div className="assistant-identity-header">
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <div className="bot-avatar-badge">
            <span className="material-symbols-outlined" style={{ fontSize: 22 }}>
              eco
            </span>
          </div>
          <div className="bot-title-block">
            <h3>NutriBot</h3>
            <p>Parametric Assessment • Milestone 1</p>
          </div>
        </div>

        <div className="verified-protocol-tag">
          <span className="material-symbols-outlined" style={{ fontSize: 15, color: "var(--primary)" }}>
            verified
          </span>
          <span>Verified Safety Protocol</span>
        </div>
      </div>

      {isGuardrailBlocked && (
        <section className="guardrail-card">
          <div className="guardrail-header">
            <div className="guardrail-label">
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>
                shield
              </span>
              <span>Guardrail Intercept: {formatGuardrailReason(message.guardrail_reason)}</span>
            </div>
            <span className="guardrail-enforced-pill">Enforced</span>
          </div>
          <div className="guardrail-content">{renderFormattedText(message.content)}</div>
        </section>
      )}

      {!isGuardrailBlocked && (
        <div className="assistant-answer-body">{renderFormattedText(message.content)}</div>
      )}

      {hasClaims && (
        <div className="claims-section">
          <div className="claims-header-row">
            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
                fact_check
              </span>
              <span>Factual Claims ({message.claims?.length}) — Milestone 1 Tracking</span>
            </div>
            <span style={{ fontSize: "0.7rem", color: "var(--outline)" }}>Click to inspect citations</span>
          </div>

          {message.claims?.map((claim, idx) => (
            <div
              key={claim.id || idx}
              className="claim-item-card"
              onClick={() => onInspectClaim && onInspectClaim(claim)}
              title="Click to view citation tracking in Sources Drawer"
            >
              <div className="claim-text-content">
                <span className="claim-index-number">[{idx + 1}]</span>
                {claim.text}
              </div>
              <span className="claim-m1-tag">
                {claim.source ? claim.source : "Unverified Citation (M1)"}
              </span>
            </div>
          ))}
        </div>
      )}

      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          paddingTop: "0.5rem",
          borderTop: "1px solid var(--surface-container-high)",
          fontSize: "0.75rem",
          color: "var(--outline)",
        }}
      >
        <button
          onClick={handleCopy}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 4,
            padding: "4px 10px",
            borderRadius: "9999px",
            background: "var(--surface-container)",
            border: "none",
            color: "var(--on-surface-variant)",
            cursor: "pointer",
            fontSize: "0.75rem",
            fontWeight: 600,
          }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: 15 }}>
            {copied ? "check" : "content_copy"}
          </span>
          <span>{copied ? "Copied" : "Copy Response"}</span>
        </button>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span>Engine: Gemini 3.1 Flash</span>
          <span>•</span>
          <span>Null Sources: Enforced</span>
        </div>
      </div>
    </article>
  );
}

function formatGuardrailReason(reason?: string | null): string {
  if (!reason) return "Clinical Safety Boundary";
  if (reason === "calorie_weight_target") return "Calorie Target Intercept";
  if (reason === "body_weight_recommendation") return "Body Weight Recommendation Intercept";
  if (reason === "medical_advice") return "Medical / Prescription Advice Intercept";
  return reason.replace(/_/g, " ").toUpperCase();
}
