"use client";

import React from "react";
import { Message, Claim } from "../lib/api";
import { ClaimBadge } from "./ClaimBadge";

interface MessageBubbleProps {
  message: Message;
  onInspectClaim?: (claim: Claim) => void;
}

export function MessageBubble({ message, onInspectClaim }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const hasClaims = message.claims && message.claims.length > 0;
  const isGuardrailBlocked = message.guardrail_triggered;

  // Simple, clean markdown-like line renderer (handles **bold**, *italic*, bullet points)
  const renderFormattedText = (text: string) => {
    const lines = text.split("\n");
    return lines.map((line, idx) => {
      if (line.trim().startsWith("- ") || line.trim().startsWith("* ")) {
        const bulletText = line.trim().substring(2);
        return (
          <li key={idx} style={{ marginLeft: "1.25rem", marginBottom: "0.25rem" }}>
            {formatSpans(bulletText)}
          </li>
        );
      }
      if (line.trim() === "") {
        return <div key={idx} style={{ height: "0.5rem" }} />;
      }
      return (
        <p key={idx} style={{ marginBottom: "0.45rem" }}>
          {formatSpans(line)}
        </p>
      );
    });
  };

  const formatSpans = (str: string) => {
    // Basic bold **text** parsing
    const parts = str.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={i} style={{ color: "#fff", fontWeight: 600 }}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  return (
    <div className={`message-wrapper ${isUser ? "user" : "bot"}`}>
      <div className={`avatar ${isUser ? "user" : "bot"}`}>
        {isUser ? "👤" : "🥗"}
      </div>

      <div className="message-content-box">
        <div
          className={`message-bubble ${isUser ? "user" : "bot"} ${
            isGuardrailBlocked ? "guardrail-blocked" : ""
          }`}
        >
          {isGuardrailBlocked && (
            <div className="guardrail-badge-box">
              <span>🛡️</span>
              <span>Guardrail Intercepted: {formatGuardrailReason(message.guardrail_reason)}</span>
            </div>
          )}

          <div>{renderFormattedText(message.content)}</div>

          {!isUser && hasClaims && (
            <div className="claims-container">
              <div className="claims-title">
                <span>📋</span>
                <span>Factual Claims ({message.claims?.length}) — Unverified (M1)</span>
              </div>
              {message.claims?.map((claim, idx) => (
                <ClaimBadge
                  key={claim.id || idx}
                  claim={claim}
                  index={idx}
                  onInspect={onInspectClaim}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function formatGuardrailReason(reason?: string | null): string {
  if (!reason) return "Safety Filter";
  if (reason === "calorie_weight_target") return "Calorie Intake Target Blocked";
  if (reason === "body_weight_recommendation") return "Body Weight Recommendation Blocked";
  if (reason === "medical_advice") return "Medical / Prescription Advice Blocked";
  return reason.replace(/_/g, " ").toUpperCase();
}
