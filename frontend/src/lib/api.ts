// ============================================================
// API Client - Backend Communication
// ============================================================

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}

// ============================================================
// Types
// ============================================================

export interface Material {
  id: string;
  title: string;
  status: string;
  source_url: string | null;
  file_key: string | null;
}

export interface WikiEntry {
  id: string;
  title: string;
  content: string;
}

export interface Citation {
  id: string;
  title: string;
}

export interface AskResponse {
  answer: string;
  citations: Citation[];
}

// ============================================================
// API Methods
// ============================================================

export const api = {
  // Ingestion
  ingestURL: (url: string) =>
    apiFetch<Material>("/ingest/url", {
      method: "POST",
      body: JSON.stringify({ url }),
    }),

  ingestUpload: async (file: File, title?: string): Promise<Material> => {
    const formData = new FormData();
    formData.append("file", file);
    if (title) formData.append("title", title);

    const res = await fetch(`${BASE}/ingest/upload`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      throw new Error(`API error: ${res.status}`);
    }

    return res.json();
  },

  // Wiki
  wikiEntry: (id: string) => apiFetch<WikiEntry>(`/wiki/${id}`),

  // Q&A
  ask: (question: string): Promise<AskResponse> =>
    apiFetch("/ask", {
      method: "POST",
      body: JSON.stringify({ question }),
    }),

  // Export
  exportZip: () => `${BASE}/export`,
};