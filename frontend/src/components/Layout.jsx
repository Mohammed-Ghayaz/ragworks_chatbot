import React from "react";

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-white text-slate-900">
      <main className="max-w-5xl mx-auto p-6">{children}</main>
    </div>
  );
}
