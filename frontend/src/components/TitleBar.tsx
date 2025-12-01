export function Header() {
  return (
    <header className="w-full bg-[#0d1117] border-b border-gray-800/50 sticky top-0 z-50 py-4">
      <div className="max-w-[1800px] mx-auto px-6 flex items-center justify-between">
        {/* Left: Logo */}
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 bg-gradient-to-b from-cyan-400 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white leading-tight">Factor</h1>
            <h1 className="text-2xl font-bold text-white leading-tight -mt-1">Flow</h1>
          </div>
        </div>

        {/* Center: Navigation */}
        <nav className="hidden lg:flex items-center gap-2">
          <button className="relative px-5 py-2.5 text-white font-medium flex items-center gap-2 group">
            <span className="text-lg">📊</span>
            <span>Analytics Dashboard</span>
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-500"></span>
          </button>
          <button className="px-5 py-2.5 text-gray-400 font-medium hover:text-white transition-colors flex items-center gap-2">
            <span className="text-lg">🏛️</span>
            <span>Nations</span>
            <span className="text-[10px] px-2 py-0.5 bg-gray-800/80 text-gray-400 rounded-full border border-gray-700">Coming Soon</span>
          </button>
          <button className="px-5 py-2.5 text-gray-400 font-medium hover:text-white transition-colors flex items-center gap-2">
            <span className="text-lg">🎯</span>
            <span>Prediction</span>
            <span className="text-[10px] px-2 py-0.5 bg-gray-800/80 text-gray-400 rounded-full border border-gray-700">Coming Soon</span>
          </button>
        </nav>

        {/* Right: Profile/Actions */}
        <div className="flex items-center gap-3">
          <span className="hidden md:block text-gray-300 font-medium mr-2">joonha park</span>
          <button className="hidden md:flex px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-lg hover:bg-emerald-500/20 text-sm font-medium transition-colors">
            Community
          </button>
          <button className="hidden lg:flex items-center gap-2 px-4 py-2 bg-[#1a1f2e] border border-indigo-500/30 text-indigo-300 rounded-lg hover:bg-[#252b3b] text-sm font-medium transition-colors">
            <span>👤</span> Edit profile
          </button>
          <button className="hidden lg:flex px-4 py-2 bg-[#1a1f2e] border border-yellow-500/30 text-yellow-400 rounded-lg hover:bg-[#252b3b] text-sm font-medium transition-colors">
            Sign out
          </button>
          <button className="hidden xl:flex items-center gap-2 px-4 py-2 bg-[#1a1f2e] border border-cyan-500/30 text-cyan-400 rounded-lg hover:bg-[#252b3b] text-sm font-medium transition-colors">
            <span>📊</span> Factor List
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-[#1a1f2e] border border-gray-700 text-gray-300 rounded-lg hover:bg-[#252b3b] text-sm font-medium transition-colors">
            <span>💬</span> Support
          </button>
        </div>
      </div>
    </header>
  );
}
