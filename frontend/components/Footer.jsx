import Link from "next/link";

export default function Footer({ showNav = true }) {
  return (
    <footer className="border-t border-gray-200 bg-panel-muted px-6 py-4">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-sm">
        <p className="font-semibold text-ink">PaperInsight</p>
        {showNav ? (
          <p className="text-ink-soft text-xs">
            Professional manuscript quality infrastructure for academic
            institutions.
          </p>
        ) : (
          <nav className="flex gap-4 text-xs text-ink-soft">
            <Link href="/" className="hover:text-brand transition-colors">
              Home
            </Link>
            <Link href="/student" className="hover:text-brand transition-colors">
              Student
            </Link>
            <Link href="/professor" className="hover:text-brand transition-colors">
              Professor
            </Link>
          </nav>
        )}
      </div>
    </footer>
  );
}
