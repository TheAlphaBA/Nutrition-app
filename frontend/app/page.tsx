"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Claim,
  ConversationSummary,
  Message,
  checkBackendHealth,
  fetchConversation,
  fetchConversations,
  sendChatMessage,
} from "../lib/api";
import { Header } from "../components/Header";
import { Sidebar } from "../components/Sidebar";
import { ChatWindow } from "../components/ChatWindow";
import { SourcesPanel } from "../components/SourcesPanel";

export default function Home() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSourcesOpen, setIsSourcesOpen] = useState<boolean>(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [backendOnline, setBackendOnline] = useState<boolean>(true);

  // Load conversations on mount
  const loadConversations = useCallback(async () => {
    const list = await fetchConversations();
    setConversations(list);
  }, []);

  useEffect(() => {
    loadConversations();
    checkBackendHealth().then((res) => {
      setBackendOnline(res.status === "ok");
    });
  }, [loadConversations]);

  // Load selected conversation
  const handleSelectConversation = async (id: string) => {
    setActiveConversationId(id);
    const detail = await fetchConversation(id);
    if (detail) {
      setMessages(detail.messages);
    }
  };

  // Start new consultation
  const handleNewChat = () => {
    setActiveConversationId(null);
    setMessages([]);
  };

  // Send message
  const handleSendMessage = async (userText: string) => {
    if (!userText.trim() || isLoading) return;

    // Optimistically add user message
    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: userText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(userText, activeConversationId);

      const botMsg: Message = {
        id: response.message_id,
        role: "assistant",
        content: response.answer,
        created_at: new Date().toISOString(),
        claims: response.claims,
        guardrail_triggered: response.guardrail_triggered,
        guardrail_reason: response.guardrail_reason,
      };

      setMessages((prev) => [...prev, botMsg]);

      if (!activeConversationId && response.conversation_id) {
        setActiveConversationId(response.conversation_id);
      }

      // Refresh sidebar conversation list
      loadConversations();
    } catch (err: unknown) {
      const errorText = err instanceof Error ? err.message : "Failed to connect to assistant.";
      const errorMsg: Message = {
        id: `err-${Date.now()}`,
        role: "assistant",
        content: `⚠️ **Connection Error**: ${errorText}\n\nPlease verify that the FastAPI backend server is running on \`http://localhost:8000\`.`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  // Extract all claims from current conversation for Sources Panel
  const allCurrentClaims: Claim[] = messages.reduce<Claim[]>((acc, msg) => {
    if (msg.claims && msg.claims.length > 0) {
      return [...acc, ...msg.claims];
    }
    return acc;
  }, []);

  // Compute active title for header
  const activeSummary = conversations.find((c) => c.id === activeConversationId);
  const activeTitle = activeSummary ? activeSummary.preview : "Nutritional Inquiry Workspace";

  return (
    <div className="app-container">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        isOpen={isSidebarOpen}
      />

      <div style={{ flex: 1, display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" }}>
        <Header
          activeTitle={activeTitle}
          sourcesCount={allCurrentClaims.length}
          isSourcesOpen={isSourcesOpen}
          onToggleSources={() => setIsSourcesOpen((prev) => !prev)}
          onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
          backendOnline={backendOnline}
        />

        <div style={{ flex: 1, display: "flex", height: "calc(100% - 64px)", overflow: "hidden" }}>
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
            onInspectClaim={() => setIsSourcesOpen(true)}
          />

          <SourcesPanel
            claims={allCurrentClaims}
            isOpen={isSourcesOpen}
            onClose={() => setIsSourcesOpen(false)}
          />
        </div>
      </div>
    </div>
  );
}
