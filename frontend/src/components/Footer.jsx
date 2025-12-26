import React from "react";

export default function Footer() {
  return (
    <footer className="mt-12 py-6 text-center text-sm text-slate-500">
      <div className="max-w-5xl mx-auto">© {new Date().getFullYear()} RAGWorks — Built with ❤️</div>
    </footer>
  );
}
