import Link from "next/link";
import Footer from "./Footer";

export default function DashboardShell({ caption, children }) {
  return (
    <div className="min-h-screen flex flex-col bg-[#f8fafc]">
      {/* Top bar */}
      <header className="bg-[#0f172a] text-white">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-3">
            <span className="w-9 h-9 rounded-lg bg-gradient-to-br from-brand-light to-brand-dark text-white text-xs font-bold flex items-center justify-center">
              PI
            </span>
            <span>
              <span className="block text-sm font-bold leading-tight">PaperInsight</span>
              <span className="block text-[11px] text-blue-200 leading-tight">{caption}</span>
            </span>
          </Link>
          <Link
            href="/"
            className="text-sm text-blue-200 hover:text-white transition-colors"
          >
            Back to Home
          </Link>
        </div>
      </header>

      {/* Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 flex flex-col gap-5">
        {children}
      </main>

      <Footer showNav={false} />
    </div>
  );
}
