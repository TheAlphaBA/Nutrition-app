"use client";

import React, { useRef, useEffect } from "react";
import { Message, Claim } from "../lib/api";
import { MessageBubble } from "./MessageBubble";
import { InputBar } from "./InputBar";

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
    <div className="main-chat">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-hero">
            <div className="hero-icon">🥗</div>
            <h2>AI Nutrition Assistant</h2>
            <p>
              Ask evidence-based questions about whole foods, nutrient retention, food safety storage,
              and cooking techniques. Every claim is extracted and tracked for Milestone 2 verification.
            </p>

            <div className="safety-notes-grid">
              <div className="safety-card">
                <strong>🔬 Claim Extraction (M1)</strong>
                Answers are broken down into individual factual claims with citation status tracked.
              </div>
              <div className="safety-card">
                <strong>🛡️ Code Guardrails</strong>
                Code strictly refuses personalized calorie targets, body weight advice, and medical diagnoses.
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
              <div className="message-wrapper bot">
                <div className="avatar bot">🥗</div>
                <div className="message-content-box">
                  <div className="message-bubble bot" style={{ display: "inline-flex" }}>
                    <div className="typing-indicator">
                      <span className="typing-dot" />
                      <span className="typing-dot" />
                      <span className="typing-dot" />
                    </div>
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
