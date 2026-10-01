"use client";

import React from "react";
import { ConversationSummary } from "../lib/api";
import { NutriBotLogo } from "./NutriBotLogo";

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
  if (!isOpen) return null;

  return (
    <aside className="sidebar">
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        <div className="sidebar-brand">
          <NutriBotLogo className="h-9 w-auto" />
          <div style={{ display: "flex", flexDirection: "column", marginLeft: 4 }}>
            <span style={{ fontSize: "0.65rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--secondary)" }}>
              Food Safety AI
            </span>
          </div>
        </div>

        <button className="sidebar-new-btn" onClick={onNewChat}>
          <span className="material-symbols-outlined" style={{ fontSize: 18 }}>add</span>
          <span>New Consultation</span>
        </button>

        <div className="recent-inquiries-label">
          <span>Recent Inquiries</span>
          <span className="material-symbols-outlined" style={{ fontSize: 16 }}>history</span>
        </div>

        <nav className="conversation-nav">
          {conversations.length === 0 ? (
            <div style={{ padding: "1.5rem 0.5rem", textAlign: "center", color: "var(--outline)", fontSize: "0.8rem" }}>
              No previous consultations. Ask a question to begin.
            </div>
          ) : (
            conversations.map((conv) => {
              const isActive = conv.id === activeConversationId;
              const dateStr = formatRelativeDate(conv.updated_at);

              return (
                <button
                  key={conv.id}
                  className={`conversation-card ${isActive ? "active" : ""}`}
                  onClick={() => onSelectConversation(conv.id)}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 4 }}>
                    <span className="conversation-title">{conv.preview || "Nutritional Inquiry"}</span>
                    <span style={{
                      fontSize: "0.65rem",
                      padding: "2px 6px",
                      borderRadius: "9999px",
                      background: isActive ? "var(--secondary-container)" : "var(--surface-container-high)",
                      color: isActive ? "var(--on-secondary-container)" : "var(--outline)",
                      fontWeight: 600,
                    }}>
                      {dateStr}
                    </span>
                  </div>
                  <span className="conversation-sub">
                    <span>{conv.message_count} messages</span>
                    <span>Ref: #{conv.id.slice(-4)}</span>
                  </span>
                </button>
              );
            })
          )}
        </nav>
      </div>

      <div className="sidebar-footer">
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: "50%",
            background: "var(--primary-fixed)",
            color: "var(--on-primary-fixed)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}>
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>person</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <span style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--on-surface)", lineHeight: 1.2 }}>
              Consultation Mode
            </span>
            <span style={{ fontSize: "0.7rem", color: "var(--outline)" }}>
              Parametric Memory (M1)
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}

function formatRelativeDate(dateStr: string): string {
  const d = new Date(dateStr);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - d.getTime()) / (1000 * 3600 * 24));
  if (diffDays <= 0) return "Today";
  if (diffDays === 1) return "1d ago";
  if (diffDays < 7) return `${diffDays}d ago`;
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}
