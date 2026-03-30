import Link from "next/link";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-line">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-3 group">
          <span className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-light to-brand-dark text-white text-sm font-bold flex items-center justify-center">
            PI
          </span>
          <span>
            <span className="block text-[15px] font-bold text-ink leading-tight">
              PaperInsight
            </span>
            <span className="block text-[11px] text-ink-soft leading-tight">
              Research Quality Platform
            </span>
          </span>
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-7">
          <a href="#platform" className="text-sm font-semibold text-gray-600 hover:text-brand transition-colors">
            Platform
          </a>
          <a href="#capabilities" className="text-sm font-semibold text-gray-600 hover:text-brand transition-colors">
            Capabilities
          </a>
          <a href="#roles" className="text-sm font-semibold text-gray-600 hover:text-brand transition-colors">
            Dashboards
          </a>
          <a href="#coverage" className="text-sm font-semibold text-gray-600 hover:text-brand transition-colors">
            Coverage
          </a>
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <Link
            href="/student"
            className="hidden sm:inline-flex px-4 py-2 text-sm font-semibold rounded-lg border border-line text-ink hover:border-brand hover:text-brand transition-all"
          >
            Student
          </Link>
          <Link
            href="/professor"
            className="px-4 py-2 text-sm font-semibold rounded-lg bg-gradient-to-r from-brand to-brand-dark text-white hover:shadow-lift transition-all"
          >
            Professor
          </Link>
        </div>
      </div>
    </header>
  );
}
