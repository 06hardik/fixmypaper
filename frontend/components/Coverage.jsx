"use client";

import { getCheckNamesByCategory } from "@/lib/data";

const checksByCategory = getCheckNamesByCategory();

export default function Coverage() {
  return (
    <section id="coverage" className="bg-white border border-line rounded-2xl p-6 lg:p-8">
      <div className="mb-6">
        <h2 className="text-xl font-bold">Coverage categories</h2>
        <p className="text-sm text-ink-soft mt-1">
          Quality checks available in the current platform build.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(checksByCategory).map(([cat, names]) => (
          <div
            key={cat}
            className="border border-gray-200 bg-panel-muted rounded-xl p-4"
          >
            <h4 className="text-sm font-bold mb-3">{cat}</h4>
            <div className="flex flex-wrap gap-1.5">
              {names.map((n) => (
                <span
                  key={n}
                  className="text-[11px] text-gray-600 bg-white border border-gray-200 rounded-full px-2.5 py-1"
                >
                  {n}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
