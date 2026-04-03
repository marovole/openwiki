// ============================================================
// Inbox Page - Material Ingestion
// ============================================================

"use client";

import { useState, useCallback, useEffect } from "react";
import { api, type Material } from "@/lib/api";

// ============================================================
// Material Card Component
// ============================================================

const statusColors: Record<string, string> = {
  pending: "bg-yellow-900/50 text-yellow-300 border-yellow-700",
  compiling: "bg-blue-900/50 text-blue-300 border-blue-700",
  compiled: "bg-green-900/50 text-green-300 border-green-700",
  failed: "bg-red-900/50 text-red-300 border-red-700",
};

function MaterialCard({ material }: { material: Material }) {
  return (
    <div className="flex items-center justify-between p-4 border border-zinc-800 rounded-lg bg-zinc-900/50">
      <div className="min-w-0 flex-1">
        <h3 className="font-medium truncate">{material.title}</h3>
        {material.source_url && (
          <p className="text-xs text-zinc-500 mt-1 truncate">
            {material.source_url}
          </p>
        )}
      </div>
      <span
        className={`text-xs px-2 py-1 rounded border ml-4 ${
          statusColors[material.status] || "bg-zinc-800 text-zinc-400"
        }`}
      >
        {material.status}
      </span>
    </div>
  );
}

// ============================================================
// Inbox Page
// ============================================================

export default function InboxPage() {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 加载已有 materials
  useEffect(() => {
    let mounted = true;

    async function loadMaterials() {
      try {
        const result = await api.listMaterials({ limit: 50 });
        if (mounted) {
          setMaterials(result.items);
        }
      } catch (err) {
        // 静默失败，首次加载失败不阻塞用户操作
        console.error("Failed to load materials:", err);
      } finally {
        if (mounted) {
          setInitialLoading(false);
        }
      }
    }

    loadMaterials();

    // 每 30 秒刷新一次状态（编译中的 material 可能状态变更）
    const interval = setInterval(loadMaterials, 30000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const handleIngest = useCallback(async () => {
    if (!url.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const result = await api.ingestURL(url);
      setMaterials((prev) => [result, ...prev]);
      setUrl("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to ingest URL");
    } finally {
      setLoading(false);
    }
  }, [url]);

  const handleFileUpload = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      setLoading(true);
      setError(null);

      try {
        const result = await api.ingestUpload(file);
        setMaterials((prev) => [result, ...prev]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to upload file");
      } finally {
        setLoading(false);
        e.target.value = "";
      }
    },
    []
  );

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Inbox</h1>
        <p className="text-zinc-500 mt-1">
          Add URLs or upload files to build your knowledge base
        </p>
      </div>

      {/* Ingestion Form */}
      <div className="space-y-4">
        <div className="flex gap-3">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/article"
            className="flex-1 px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-lg focus:outline-none focus:border-zinc-700 text-sm"
            onKeyDown={(e) => e.key === "Enter" && handleIngest()}
          />
          <button
            onClick={handleIngest}
            disabled={loading || !url.trim()}
            className="px-4 py-2 bg-white text-black rounded-lg font-medium text-sm hover:bg-zinc-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Adding..." : "Add URL"}
          </button>
        </div>

        {/* File Upload */}
        <div className="flex items-center gap-3">
          <span className="text-zinc-500 text-sm">or</span>
          <label className="px-4 py-2 border border-zinc-800 rounded-lg cursor-pointer hover:bg-zinc-900 transition-colors text-sm">
            Upload File
            <input
              type="file"
              accept=".md,.txt,.markdown"
              onChange={handleFileUpload}
              className="hidden"
              disabled={loading}
            />
          </label>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-900/20 border border-red-800 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}

      {/* Materials List */}
      <div className="space-y-3">
        {initialLoading ? (
          <div className="text-center py-12 text-zinc-500">
            <p>Loading...</p>
          </div>
        ) : materials.length === 0 ? (
          <div className="text-center py-12 text-zinc-500">
            <p>No materials yet</p>
            <p className="text-sm mt-1">Add a URL or upload a file to get started</p>
          </div>
        ) : (
          materials.map((material) => (
            <MaterialCard key={material.id} material={material} />
          ))
        )}
      </div>
    </div>
  );
}