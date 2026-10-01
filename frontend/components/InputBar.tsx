"use client";

import React, { useState, useRef, useEffect } from "react";

interface InputBarProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const STITCH_SUGGESTIONS = [
  "What vitamins does spinach contain?",
  "How long can cooked rice be safely stored in the fridge?",
  "Does boiling vegetables destroy their nutrients?",
  "What is the recommended daily intake of protein for 70kg?",
  "How much iron do women need compared to men?",
  "Test Guardrail: How many calories should I eat to lose weight?",
  "Test Guardrail: What supplement should I take for iron deficiency?",
];

export function InputBar({ onSendMessage, isLoading }: InputBarProps) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [text]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;
    onSendMessage(trimmed);
    setText("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="bottom-input-container">
      <div className="suggestion-pebbles-scroll">
        {STITCH_SUGGESTIONS.map((item, idx) => (
          <button
            key={idx}
            className="suggestion-pebble"
            onClick={() => !isLoading && onSendMessage(item)}
            disabled={isLoading}
          >
            {item}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="floating-input-card">
        <textarea
          ref={textareaRef}
          className="natural-textarea"
          rows={1}
          placeholder="Ask a question about food safety, nutrients, or culinary chemistry..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />

        <button
          type="submit"
          className="send-action-btn"
          disabled={!text.trim() || isLoading}
          aria-label="Send inquiry"
          title="Send consultation inquiry (Enter)"
        >
          {isLoading ? (
            <span
              className="material-symbols-outlined animate-spin"
              style={{ fontSize: 20, animation: "spin 1s linear infinite" }}
            >
              progress_activity
            </span>
          ) : (
            <span className="material-symbols-outlined" style={{ fontSize: 20 }}>
              arrow_upward
            </span>
          )}
        </button>
      </form>
    </div>
  );
}
