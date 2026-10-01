"use client";

import React from "react";
import { ConversationSummary } from "../lib/api";

interface SidebarProps {
  conversations: ConversationSummary[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  isOpen: boolean;
}

export function Sidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  isOpen,
}: SidebarProps) {
  return (
    <aside
      className="sidebar"
      style={{
        display: isOpen ? "flex" : "none",
      }}
    >
      <div className="sidebar-header">
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span style={{ fontSize: "1.2rem" }}>🌱</span>
          <span style={{ fontWeight: 700, fontSize: "0.95rem" }}>Consultations</span>
        </div>
        <span
          style={{
            fontSize: "0.75rem",
            color: "var(--text-muted)",
            background: "rgba(255,255,255,0.06)",
            padding: "2px 8px",
            borderRadius: "12px",
          }}
        >
          {conversations.length}
        </span>
      </div>

      <button className="new-chat-btn" onClick={onNewChat}>
        <span style={{ fontSize: "1.1rem" }}>+</span>
        New Consultation
      </button>

      <div className="conversation-list">
        {conversations.length === 0 ? (
          <div
            style={{
              padding: "2rem 1rem",
              textAlign: "center",
              color: "var(--text-muted)",
              fontSize: "0.8rem",
            }}
          >
            No previous conversations. Start a new one!
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === activeConversationId;
            const dateStr = new Date(conv.updated_at).toLocaleDateString(undefined, {
              month: "short",
              day: "numeric",
            });

            return (
              <button
                key={conv.id}
                className={`conversation-item ${isActive ? "active" : ""}`}
                onClick={() => onSelectConversation(conv.id)}
              >
                <span className="conversation-item-preview">
                  {conv.preview || "Nutrition discussion"}
                </span>
                <span className="conversation-item-meta">
                  {conv.message_count} messages • {dateStr}
                </span>
              </button>
            );
          })
        )}
      </div>
    </aside>
  );
}
