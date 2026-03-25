import Link from "next/link";

const roles = [
  {
    tag: "Student Dashboard",
    title: "Draft Quality Workspace",
    desc: "Upload papers, run analysis, and review section-wise quality findings in a clean interface.",
    href: "/student",
    cta: "Launch workspace",
  },
  {
    tag: "Professor Dashboard",
    title: "Governance & Format Control",
    desc: "Create approved formats, enforce required sections, and guide consistent submissions.",
    href: "/professor",
    cta: "Launch workspace",
  },
];

export default function Roles() {
  return (
    <section id="roles" className="bg-white border border-line rounded-2xl p-6 lg:p-8">
      <div className="mb-6">
        <h2 className="text-xl font-bold">Choose your role</h2>
        <p className="text-sm text-ink-soft mt-1">
          Two focused dashboards built for different responsibilities.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        {roles.map((r) => (
          <Link
            key={r.tag}
            href={r.href}
            className="group block border border-gray-200 rounded-xl p-6 bg-white hover:border-brand/40 hover:shadow-card transition-all duration-200"
          >
            <span className="inline-block text-[11px] font-bold uppercase tracking-wider text-brand-dark bg-blue-50 px-2.5 py-1 rounded-full mb-3">
              {r.tag}
            </span>
            <h3 className="font-bold text-base mb-2">{r.title}</h3>
            <p className="text-sm text-ink-soft leading-relaxed mb-4">{r.desc}</p>
            <span className="text-sm font-semibold text-brand-dark group-hover:underline">
              {r.cta} &rarr;
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}
