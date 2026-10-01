"use client";

import React, { useRef, useEffect } from "react";
import { Message, Claim } from "../lib/api";
import { MessageBubble } from "./MessageBubble";
import { InputBar } from "./InputBar";
import { NutriBotLogo } from "./NutriBotLogo";

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (message: string) => void;
  onInspectClaim?: (claim: Claim) => void;
}

export function ChatWindow({
  messages,
  isLoading,
  onSendMessage,
  onInspectClaim,
}: ChatWindowProps) {
  const scrollEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="chat-workspace">
      <div className="messages-stream">
        {messages.length === 0 ? (
          <div className="hero-welcome">
            <div className="hero-logo-box">
              <NutriBotLogo className="h-10 w-auto" />
            </div>

            <h2 className="hero-title">Nutritional Editorial &amp; Organic Intelligence</h2>
            <p className="hero-subtitle">
              Synthesizing biochemical food safety, nutrient bioavailability, and cooking thermodynamics
              into structured, verifiable dietary guidance. Every factual claim is isolated for Milestone 2 RAG verification.
            </p>

            <div className="hero-guidelines-grid">
              <div className="guideline-card">
                <strong>🔬 Claim Extraction Protocol</strong>
                <p>Every response is decomposed into standalone factual claims with null citations in Milestone 1.</p>
              </div>
              <div className="guideline-card">
                <strong>🛡️ Deterministic Safety Guardrails</strong>
                <p>Code pre-filters strictly intercept calorie targets, body weight goals, and medical prescriptions.</p>
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                onInspectClaim={onInspectClaim}
              />
            ))}

            {isLoading && (
              <div className="assistant-card" style={{ padding: "1.25rem 1.5rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <div className="bot-avatar-badge">
                    <span className="material-symbols-outlined" style={{ fontSize: 20 }}>
                      eco
                    </span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ fontSize: "0.9rem", color: "var(--on-surface-variant)", fontWeight: 500 }}>
                      Synthesizing nutritional assessment...
                    </span>
                    <span
                      style={{
                        width: 8,
                        height: 8,
                        borderRadius: "50%",
                        background: "var(--primary)",
                        animation: "pulseDot 1.2s infinite ease-in-out",
                      }}
                    />
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={scrollEndRef} />
      </div>

      <InputBar onSendMessage={onSendMessage} isLoading={isLoading} />
    </div>
  );
}
