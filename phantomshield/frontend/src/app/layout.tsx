import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PhantomShield (GraphShield AI) — GraphOps & AI Deception Platform",
  description: "Autonomous Threat Hunting, AI Deception, and Real-Time Blast Radius Containment for SOCs | hackFront India 2026",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#050811] text-slate-100 min-h-screen antialiased selection:bg-cyan-500 selection:text-black">
        {children}
      </body>
    </html>
  );
}

