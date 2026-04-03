// ============================================================
// Navigation Component
// ============================================================

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/inbox", label: "Inbox" },
  { href: "/wiki", label: "Wiki" },
  { href: "/ask", label: "Ask" },
];

export function Nav() {
  const path = usePathname();
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  return (
    <nav className="flex gap-6 px-6 py-4 border-b border-zinc-800 bg-zinc-950">
      <span className="font-bold text-lg tracking-tight">OpenWiki</span>

      <div className="flex gap-4 ml-8">
        {links.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            className={`text-sm transition-colors ${
              path.startsWith(l.href)
                ? "text-white"
                : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            {l.label}
          </Link>
        ))}
      </div>

      <a
        href={`${apiUrl}/export`}
        className="ml-auto text-sm text-zinc-500 hover:text-zinc-300 transition-colors"
      >
        Export
      </a>
    </nav>
  );
}