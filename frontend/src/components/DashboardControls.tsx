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
      {/* Bubble-like Container with lighter background to stand out from main page */}
      <div className="bg-[#131b26] rounded-[2.5rem] p-12 border border-white/5 shadow-2xl">
        {/* Top Row: Title and Time Frames */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
          <h1 className="text-7xl font-bold text-white tracking-tight">
            Analytics Dashboard
          </h1>
          
          {/* Time Frame Switcher - Aligned to bottom right relative to title */}
          <div className="flex bg-[#1e2330] rounded-lg p-1.5 border border-white/5 self-start md:self-end">
            {TIME_FRAMES.map((tf) => (
              <button
                key={tf}
                onClick={() => setSelectedTimeFrame(tf)}
                className={`px-6 py-2.5 rounded-md text-base font-bold transition-all ${
                  selectedTimeFrame === tf
                    ? 'bg-cyan-500 text-black shadow-lg shadow-cyan-500/20'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        {/* Bottom Row: Metadata & Controls */}
        <div className="flex flex-wrap items-center gap-10 text-base font-medium">
          {/* Definitions Button */}
          <button 
            onClick={() => setIsDefinitionsOpen(true)}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[#252b3b] border border-purple-500/20 text-purple-400 hover:bg-[#2a3140] transition-colors hover:border-purple-500/40"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <span>Definitions</span>
          </button>

          {/* Live Feed Indicator */}
          <div className="flex items-center gap-3 text-gray-400">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <span>Live Feed</span>
          </div>

          {/* Date */}
          <div className="text-gray-400 flex items-center gap-3">
            <span className="text-gray-600 text-sm">•</span>
            <span>As of {currentDate}</span>
          </div>

          {/* Active Factors Count (Clickable) */}
          <button 
            onClick={() => setIsFactorsOpen(true)}
            className="text-gray-400 hover:text-white transition-colors flex items-center gap-3 group"
          >
            <span className="text-gray-600 text-sm">•</span>
            <span className="group-hover:underline decoration-gray-600 underline-offset-4">
              {factors.length > 0 ? factors.length : '204'} Active Factors
            </span>
          </button>
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
