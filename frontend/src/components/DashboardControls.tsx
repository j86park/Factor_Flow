import { useState, useEffect } from 'react';
import { Modal } from './Modal';

interface Definition {
  term: string;
  description: string;
  example: string;
}

interface Factor {
  name: string;
  description: string;
  category: string;
}

const TIME_FRAMES = ['1D', '5D', '1M', '3M', '6M', '12M'];

export function DashboardControls() {
  const [selectedTimeFrame, setSelectedTimeFrame] = useState('1D');
  const [isDefinitionsOpen, setIsDefinitionsOpen] = useState(false);
  const [isFactorsOpen, setIsFactorsOpen] = useState(false);
  
  const [definitions, setDefinitions] = useState<Definition[]>([]);
  const [factors, setFactors] = useState<Factor[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentDate, setCurrentDate] = useState('');

  // Fetch data from backend and set date
  useEffect(() => {
    // Set initial date
    const now = new Date();
    setCurrentDate(now.toISOString().split('T')[0]);

    const fetchData = async () => {
      setIsLoading(true);
      try {
        // In production, replace with your actual deployed backend URL if needed,
        // or rely on relative paths if proxied. For now assuming localhost or same origin.
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        
        const [defsRes, factorsRes] = await Promise.all([
          fetch(`${baseUrl}/api/definitions`),
          fetch(`${baseUrl}/api/factors`)
        ]);

        if (defsRes.ok) {
          setDefinitions(await defsRes.json());
        }
        if (factorsRes.ok) {
          setFactors(await factorsRes.json());
        }
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();

    // Optional: Update date if day changes while page is open (check every minute)
    const interval = setInterval(() => {
        const newDate = new Date().toISOString().split('T')[0];
        setCurrentDate(prev => newDate !== prev ? newDate : prev);
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full mb-6">
      {/* Bubble-like Container */}
      <div className="bg-[#131b26] rounded-[3rem] p-12 border border-white/5 shadow-2xl relative overflow-hidden">
        {/* Subtle background glow/gradient */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 pointer-events-none"></div>

        {/* Top Row: Title */}
        <div className="mb-16 relative z-10">
          <h1 className="text-7xl md:text-8xl font-bold text-white tracking-tight drop-shadow-lg">
            Analytics Dashboard
          </h1>
        </div>

        {/* Bottom Row: Metadata & Controls */}
        <div className="flex flex-col xl:flex-row items-start xl:items-center justify-between gap-8 text-base font-medium relative z-10">
          
          {/* Left Side: Controls & Data */}
          <div className="flex flex-wrap items-center gap-6 md:gap-10">
            {/* Definitions Button */}
            <button 
              onClick={() => setIsDefinitionsOpen(true)}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[#252b3b] border border-indigo-500/30 text-indigo-300 hover:bg-[#2a3140] hover:text-white transition-all hover:shadow-lg hover:shadow-indigo-500/10 active:scale-95"
            >
              <span className="text-lg">📚</span>
              <span>Definitions</span>
            </button>

            {/* Live Feed Indicator */}
            <div className="flex items-center gap-3 text-gray-300">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]"></span>
              </span>
              <span>Live Feed</span>
            </div>

            {/* Date */}
            <div className="text-gray-400 flex items-center gap-3">
              <span className="text-gray-600 text-xs">•</span>
              <span>As of {currentDate}</span>
            </div>

            {/* Active Factors Count */}
            <button 
              onClick={() => setIsFactorsOpen(true)}
              className="text-gray-400 hover:text-white transition-colors flex items-center gap-3 group"
            >
              <span className="text-gray-600 text-xs">•</span>
              <span className="group-hover:underline decoration-gray-500 underline-offset-4 transition-all">
                {factors.length > 0 ? factors.length : '204'} Active Factors
              </span>
            </button>
          </div>

          {/* Right Side: Time Frame Switcher */}
          <div className="flex bg-[#0f151f] rounded-xl p-1.5 border border-white/5">
            {TIME_FRAMES.map((tf) => (
              <button
                key={tf}
                onClick={() => setSelectedTimeFrame(tf)}
                className={`px-6 py-2.5 rounded-lg text-sm font-bold transition-all duration-200 ${
                  selectedTimeFrame === tf
                    ? 'bg-cyan-500 text-black shadow-[0_0_20px_rgba(6,182,212,0.3)] scale-105'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* MODALS */}
      
      {/* Definitions Modal */}
      <Modal
        isOpen={isDefinitionsOpen}
        onClose={() => setIsDefinitionsOpen(false)}
        title="Trading Definitions"
      >
        <div className="text-gray-400 mb-6">Key concepts and metrics explained</div>
        <div className="space-y-6">
          {definitions.map((def, idx) => (
            <div key={idx} className="bg-dark-bg/50 rounded-xl p-5 border border-gray-800">
              <h3 className="text-cyan-500 font-bold text-lg mb-2 bg-cyan-950/30 inline-block px-3 py-1 rounded-md">
                {def.term}
              </h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                {def.description}
              </p>
              <div className="bg-[#1e2330] rounded-lg p-4 border-l-4 border-indigo-500">
                <div className="flex items-start gap-2">
                  <span className="text-yellow-400 mt-0.5">💡</span>
                  <div>
                    <span className="text-indigo-400 text-xs font-bold uppercase tracking-wider block mb-1">Example</span>
                    <p className="text-sm text-gray-400">{def.example}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
          {definitions.length === 0 && !isLoading && (
            <p className="text-center text-gray-500 py-8">No definitions loaded.</p>
          )}
        </div>
      </Modal>

      {/* Factors Modal */}
      <Modal
        isOpen={isFactorsOpen}
        onClose={() => setIsFactorsOpen(false)}
        title="Factor Library"
        maxWidth="max-w-4xl"
      >
        <div className="text-gray-400 mb-6">{factors.length} factors available</div>
        
        <div className="relative mb-6">
            <input 
                type="text" 
                placeholder="Search factors..." 
                className="w-full bg-dark-bg border border-gray-700 rounded-lg py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
            />
            <svg className="absolute right-4 top-3.5 w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
        </div>

        <div className="space-y-3">
          {factors.map((factor, idx) => (
            <div key={idx} className="bg-dark-bg/30 hover:bg-dark-bg/50 transition-colors rounded-xl p-5 border border-gray-800">
              <h3 className="text-cyan-400 font-bold text-lg mb-1">
                {factor.name}
              </h3>
              <p className="text-gray-400 text-sm">
                {factor.description}
              </p>
            </div>
          ))}
           {factors.length === 0 && !isLoading && (
            <p className="text-center text-gray-500 py-8">No factors loaded.</p>
          )}
        </div>
      </Modal>
    </div>
  );
}
