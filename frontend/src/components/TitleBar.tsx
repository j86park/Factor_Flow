export function Header() {
  return (
    <header className="w-full bg-[#0d1117] sticky top-0 z-50 py-6">
      <div className="max-w-[1800px] mx-auto px-6 flex items-center justify-center">
        {/* Centered: Logo */}
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 bg-gradient-to-b from-cyan-400 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <h1 className="text-5xl font-bold text-white tracking-wide">
            Factor Flow
          </h1>
        </div>
      </div>
    </header>
  );
}
