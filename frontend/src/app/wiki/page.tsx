// ============================================================
// Wiki Page - Browse Knowledge Entries
// ============================================================

"use client";

import { useState, useEffect, useCallback } from "react";
import { api, type WikiEntry } from "@/lib/api";

// ============================================================
// Wiki Article Component
// ============================================================

function WikiArticle({ entry }: { entry: WikiEntry }) {
  return (
    <article className="prose prose-invert prose-zinc max-w-none">
      <h1>{entry.title}</h1>
      <div
        className="mt-6"
        dangerouslySetInnerHTML={{ __html: markdownToHtml(entry.content) }}
      />
    </article>
  );
}

function markdownToHtml(markdown: string): string {
  return markdown
    .replace(/^### (.*$)/gm, "<h3>$1</h3>")
    .replace(/^## (.*$)/gm, "<h2>$1</h2>")
    .replace(/^# (.*$)/gm, "<h1>$1</h1>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/`(.*?)`/g, "<code>$1</code>")
    .replace(/\n/g, "<br>");
}

// ============================================================
// Wiki Page
// ============================================================

export default function WikiPage() {
  const [entries, setEntries] = useState<WikiEntry[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // For now, show placeholder - would need GET /wiki endpoint
    setLoading(false);
    setEntries([]);
  }, []);

  const selectedEntry = entries.find((e) => e.id === selectedId);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-zinc-500">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-900/20 border border-red-800 rounded-lg text-red-300">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Wiki</h1>
        <p className="text-zinc-500 mt-1">
          Browse your compiled knowledge entries
        </p>
      </div>

      {entries.length === 0 ? (
        <div className="text-center py-12 text-zinc-500">
          <p>No wiki entries yet</p>
          <p className="text-sm mt-1">
            Add materials in Inbox to compile them into wiki entries
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Entry List */}
          <div className="space-y-2">
            {entries.map((entry) => (
              <button
                key={entry.id}
                onClick={() => setSelectedId(entry.id)}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${
                  selectedId === entry.id
                    ? "bg-zinc-800 border-zinc-700"
                    : "bg-zinc-900/50 border-zinc-800 hover:bg-zinc-900"
                }`}
              >
                <div className="font-medium truncate">{entry.title}</div>
              </button>
            ))}
          </div>

          {/* Entry Content */}
          <div className="lg:col-span-2">
            {selectedEntry ? (
              <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6">
                <WikiArticle entry={selectedEntry} />
              </div>
            ) : (
              <div className="flex items-center justify-center h-64 text-zinc-500 border border-zinc-800 rounded-lg">
                Select an entry to view
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}