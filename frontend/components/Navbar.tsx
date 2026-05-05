"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const path = usePathname();
  return (
    <nav style={{
      position: "fixed", top: 0, left: 0, right: 0, zIndex: 100,
      display: "flex", alignItems: "center", justifyContent: "space-between",
      padding: "16px 32px",
      background: "rgba(3,3,7,0.8)",
      backdropFilter: "blur(20px)",
      borderBottom: "1px solid #ffffff10",
    }}>
      <Link href="/" style={{ textDecoration: "none" }}>
        <span style={{ fontFamily: "var(--font-heading)", fontWeight: 700, fontSize: 20 }}>
          <span className="gradient-text">AI</span>
          <span style={{ color: "var(--text)", marginLeft: 6 }}>Clipper</span>
        </span>
      </Link>

      <div style={{ display: "flex", gap: 8 }}>
        {[
          { href: "/dashboard", label: "📊 Dashboard" },
          { href: "/connect", label: "🔗 Connect" },
        ].map(({ href, label }) => (
          <Link key={href} href={href} style={{
            padding: "8px 18px",
            borderRadius: 8,
            fontSize: 14,
            fontWeight: 500,
            color: path === href ? "var(--primary-light)" : "var(--muted)",
            background: path === href ? "rgba(124,58,237,0.15)" : "transparent",
            border: `1px solid ${path === href ? "rgba(124,58,237,0.3)" : "transparent"}`,
            textDecoration: "none",
            transition: "all 0.2s",
          }}>{label}</Link>
        ))}
      </div>
    </nav>
  );
}
