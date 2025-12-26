import React from "react";
import Footer from "./Footer";

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-white text-slate-900 flex flex-col">
      <main className="max-w-5xl mx-auto p-6 flex-1">{children}</main>
      <Footer />
    </div>
  );
}
