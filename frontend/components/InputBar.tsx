"use client";

import React, { useState, useRef, useEffect } from "react";

interface InputBarProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const SAMPLE_SUGGESTIONS = [
  "What vitamins does spinach contain?",
  "How long can cooked rice be safely stored in the fridge?",
  "Does boiling vegetables destroy their nutrients?",
  "Test Guardrail: How many calories should I eat to lose weight?",
  "Test Guardrail: What medication helps with cholesterol?",
];

export function InputBar({ onSendMessage, isLoading }: InputBarProps) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
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

  const handleSuggestionClick = (suggestion: string) => {
    if (isLoading) return;
    onSendMessage(suggestion);
  };

  return (
    <div className="input-area">
      <div className="suggestion-chips">
        {SAMPLE_SUGGESTIONS.map((s, idx) => (
          <button
            key={idx}
            className="suggestion-chip"
            onClick={() => handleSuggestionClick(s)}
            disabled={isLoading}
          >
            {s}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="input-box-wrapper">
        <textarea
          ref={textareaRef}
          className="chat-textarea"
          rows={1}
          placeholder="Ask a nutrition or food safety question... (Enter to send, Shift+Enter for newline)"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />

        <button
          type="submit"
          className="send-btn"
          disabled={!text.trim() || isLoading}
          aria-label="Send message"
        >
          {isLoading ? (
            <div className="typing-dot" style={{ background: "#fff", width: 8, height: 8 }} />
          ) : (
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          )}
        </button>
      </form>
    </div>
  );
}
