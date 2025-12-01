export function Header() {
  return (
    <header className="w-full h-20 bg-dark-bg border-b border-gray-800 sticky top-0 z-50">
      <div className="container mx-auto h-full px-4 flex items-center justify-between">
        {/* Left: Logo */}
        <div className="flex items-center gap-3">
          {/* Placeholder Logo Icon (Blue drop-like shape based on screenshot) */}
          <div className="w-10 h-10 bg-gradient-to-b from-cyan-400 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
             <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
             </svg>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-wide">
            Factor Flow
          </h1>
        </div>

        {/* Center: Navigation */}
        <nav className="hidden md:flex items-center gap-1">
          <button className="px-4 py-2 text-white font-medium border-b-2 border-cyan-500 bg-white/5 rounded-t-md">
            Analytics Dashboard
          </button>
          <button className="px-4 py-2 text-gray-400 font-medium hover:text-white transition-colors flex items-center gap-2">
            Nations <span className="text-[10px] px-1.5 py-0.5 bg-gray-800 text-gray-400 rounded-full border border-gray-700">Coming Soon</span>
          </button>
          <button className="px-4 py-2 text-gray-400 font-medium hover:text-white transition-colors flex items-center gap-2">
            Prediction <span className="text-[10px] px-1.5 py-0.5 bg-gray-800 text-gray-400 rounded-full border border-gray-700">Coming Soon</span>
          </button>
        </nav>

        {/* Right: Profile/Actions */}
        <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
                <button className="hidden lg:flex items-center gap-2 px-4 py-2 bg-[#1e2330] border border-indigo-500/30 text-indigo-300 rounded-lg hover:bg-[#252b3b] text-sm font-medium transition-colors">
                   <span>👤</span> Edit profile
                </button>
                <button className="hidden lg:flex px-4 py-2 bg-[#1e2330] border border-yellow-600/30 text-yellow-500 rounded-lg hover:bg-[#252b3b] text-sm font-medium transition-colors">
                   Sign out
                </button>
            </div>
            <div className="flex items-center gap-2">
                <button className="hidden xl:flex items-center gap-2 px-4 py-2 bg-[#1e2330] border border-cyan-500/30 text-cyan-400 rounded-lg hover:bg-[#252b3b] text-sm font-medium transition-colors">
                   <span>📊</span> Factor List
                </button>
                <button className="px-4 py-2 bg-[#1e2330] border border-gray-700 text-gray-300 rounded-lg hover:bg-[#252b3b] text-sm font-medium transition-colors">
                   💬 Support
                </button>
            </div>
        </div>
      </div>
    </header>
  );
}
