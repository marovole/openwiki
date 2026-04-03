// ============================================================
// Root Page - Redirect to Inbox
// ============================================================

import { redirect } from "next/navigation";

export default function Home() {
  redirect("/inbox");
}