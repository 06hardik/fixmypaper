import Link from "next/link";

export default function Hero() {
  return (
    <section
      id="platform"
      className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#0f2a65] to-brand text-white"
    >
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_70%_20%,rgba(59,130,246,0.25),transparent_70%)]" />

      <div className="relative grid lg:grid-cols-[1.5fr_1fr] gap-8 items-center px-8 py-16 lg:py-20 lg:px-12">
        {/* Copy */}
        <div className="max-w-2xl">
          <p className="text-xs font-bold tracking-[0.15em] uppercase text-blue-300 mb-4">
            For universities, labs &amp; research teams
          </p>
          <h1 className="text-3xl sm:text-4xl lg:text-[2.65rem] font-extrabold leading-[1.12] tracking-tight">
            Enterprise-grade manuscript quality control for academic workflows.
          </h1>
          <p className="mt-5 text-blue-100 text-base lg:text-lg leading-relaxed max-w-xl">
            Streamline submission readiness with a centralized platform that helps
            teams review, standardize, and deliver publication-ready papers.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/student"
              className="px-6 py-3 rounded-xl bg-white text-brand-dark font-semibold text-sm hover:shadow-lift transition-all"
            >
              Open Student Dashboard
            </Link>
            <Link
              href="/professor"
              className="px-6 py-3 rounded-xl border border-white/30 text-white font-semibold text-sm hover:bg-white/10 transition-all"
            >
              Open Professor Dashboard
            </Link>
          </div>

          <p className="mt-5 text-xs text-blue-300/80">
            No authentication required in this version
          </p>
        </div>

        {/* KPI card */}
        <div className="hidden lg:block">
          <div className="bg-white/[0.12] border border-blue-200/25 backdrop-blur-sm rounded-2xl p-6">
            <p className="text-[11px] font-bold tracking-[0.1em] uppercase text-blue-200 mb-5">
              Operations Snapshot
            </p>
            <div className="grid grid-cols-2 gap-5">
              {[
                ["30+", "quality controls"],
                ["2", "role dashboards"],
                ["PDF", "native workflow"],
                ["Fast", "analysis pipeline"],
              ].map(([val, label]) => (
                <div key={label}>
                  <p className="text-2xl font-extrabold">{val}</p>
                  <p className="text-xs text-blue-200 mt-0.5">{label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
