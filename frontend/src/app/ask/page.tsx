// ============================================================
// Ask Page - Conversational Q&A with Citations
// ============================================================

"use client";

import { useState, useRef, useEffect } from "react";
import { api, type AskResponse } from "@/lib/api";

// ============================================================
// Citation Component
// ============================================================

function Citation({
  citation,
  index,
}: {
  citation: AskResponse["citations"][0];
  index: number;
}) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="font-mono text-zinc-500 bg-zinc-800 px-1.5 py-0.5 rounded text-xs">
        [{index + 1}]
      </span>
      <span className="text-zinc-300 truncate">{citation.title}</span>
    </div>
  );
}

// ============================================================
// Message Component
// ============================================================

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: AskResponse["citations"];
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? "bg-white text-black"
            : "bg-zinc-900 border border-zinc-800 text-zinc-100"
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="mt-4 space-y-1.5">
            <p className="text-xs text-zinc-500 font-medium">引用来源</p>
            {message.citations.map((citation, index) => (
              <Citation key={index} citation={citation} index={index} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================
// Ask Page
// ============================================================

export default function AskPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const response = await api.ask(input.trim());

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer,
        citations: response.citations,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "提问失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-120px)]">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Ask</h1>
        <p className="text-zinc-500 mt-1">
          向你的知识库提问，获取带引用的回答
        </p>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 p-4 bg-red-900/20 border border-red-800 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-zinc-500">
            <div className="text-center">
              <p>开始提问吧</p>
              <p className="text-sm mt-1">例如："如何配置 pgvector 扩展？"</p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-zinc-500 rounded-full animate-pulse" />
                    <span className="text-zinc-500">思考中...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="mt-4">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="输入你的问题..."
            className="flex-1 px-4 py-3 bg-zinc-900 border border-zinc-800 rounded-lg focus:outline-none focus:border-zinc-700 text-sm"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-white text-black rounded-lg font-medium text-sm hover:bg-zinc-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "发送中" : "发送"}
          </button>
        </div>
      </form>
    </div>
  );
}