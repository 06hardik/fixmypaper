const cards = [
  {
    title: "Centralized Review",
    desc: "Run a complete quality check and consolidate outcomes into one consistent report.",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15a2.25 2.25 0 012.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V19.5a2.25 2.25 0 002.25 2.25h.75" />
      </svg>
    ),
  },
  {
    title: "Institution Standards",
    desc: "Define and manage custom submission formats for departments and guided cohorts.",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342" />
      </svg>
    ),
  },
  {
    title: "Actionable Output",
    desc: "Generate clear diagnostics and downloadable annotated files for rapid revision cycles.",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
      </svg>
    ),
  },
];

export default function Features() {
  return (
    <section id="capabilities" className="bg-white border border-line rounded-2xl p-6 lg:p-8">
      <div className="mb-6">
        <h2 className="text-xl font-bold">Designed for professional research operations</h2>
        <p className="text-sm text-ink-soft mt-1">
          Clear structure, measurable outputs, and role-specific workflows.
        </p>
      </div>

      <div className="grid sm:grid-cols-3 gap-4">
        {cards.map((c) => (
          <article
            key={c.title}
            className="group border border-gray-200 rounded-xl p-5 bg-panel-muted hover:border-brand/40 hover:shadow-card transition-all duration-200"
          >
            <div className="w-10 h-10 rounded-lg bg-blue-50 text-brand flex items-center justify-center mb-4 group-hover:bg-brand group-hover:text-white transition-colors">
              {c.icon}
            </div>
            <h3 className="font-semibold text-[15px] mb-1.5">{c.title}</h3>
            <p className="text-sm text-ink-soft leading-relaxed">{c.desc}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
