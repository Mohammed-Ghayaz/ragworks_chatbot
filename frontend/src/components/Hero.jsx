import React from "react";

export default function Hero({ title, subtitle, children }) {
  return (
    <section className="bg-gradient-to-r from-indigo-600 to-emerald-500 text-white rounded-lg p-8 mb-6">
      <div className="max-w-5xl mx-auto flex items-center justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold">{title}</h1>
          <p className="mt-2 text-indigo-100">{subtitle}</p>
        </div>
        <div>{children}</div>
      </div>
    </section>
  );
}
