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

  // The active factors count is now dynamically based on the fetched factors
  const activeFactorsCount = factors.length;

  useEffect(() => {
    const now = new Date();
    setCurrentDate(now.toISOString().split('T')[0]);

    const fetchData = async () => {
      setIsLoading(true);
      try {
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

    const interval = setInterval(() => {
      const newDate = new Date().toISOString().split('T')[0];
      setCurrentDate(prev => newDate !== prev ? newDate : prev);
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full mt-10">
      {/* Dashboard Card Container */}
      <div className="bg-[#151d2a] rounded-[2rem] p-10 md:p-14 shadow-2xl">
        
        {/* Title Row - Centered */}
        <h1 className="text-6xl md:text-7xl lg:text-8xl font-extrabold text-white tracking-tight mb-10 text-center">
          Analytics Dashboard
        </h1>

        {/* Controls Row - Evenly spread horizontally */}
        <div className="flex flex-wrap items-center justify-between gap-6 px-4">
          {/* Definitions Button - Dark rounded pill style */}
          <button 
            onClick={() => setIsDefinitionsOpen(true)}
            className="flex items-center gap-2.5 px-6 py-3 rounded-full bg-[#1a2332] text-gray-300 hover:bg-[#232d3f] transition-all text-sm font-medium"
          >
            <span className="text-base">📚</span>
            <span>Definitions</span>
          </button>

          {/* Live Feed Indicator */}
          <div className="flex items-center gap-2.5 text-gray-300 text-sm">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span>Live Feed</span>
          </div>

          {/* Date */}
          <span className="text-gray-400 text-sm">As of {currentDate}</span>

          {/* Active Factors - Dark rounded pill style */}
          <button 
            onClick={() => setIsFactorsOpen(true)}
            className="px-6 py-3 rounded-full bg-[#1a2332] text-gray-300 hover:bg-[#232d3f] transition-all text-sm font-medium"
          >
            {activeFactorsCount} Active Factors
          </button>

          {/* Time Frame Switcher - Rounded pills with cyan highlight */}
          <div className="flex gap-2">
            {TIME_FRAMES.map((tf) => (
              <button
                key={tf}
                onClick={() => setSelectedTimeFrame(tf)}
                className={`px-5 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                  selectedTimeFrame === tf
                    ? 'bg-cyan-500 text-black'
                    : 'bg-[#1a2332] text-gray-400 hover:text-white hover:bg-[#232d3f]'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* MODALS */}
      <Modal
        isOpen={isDefinitionsOpen}
        onClose={() => setIsDefinitionsOpen(false)}
        title="Trading Definitions"
      >
        <div className="text-gray-400 mb-6">Key concepts and metrics explained</div>
        <div className="space-y-6">
          {definitions.map((def, idx) => (
            <div key={idx} className="bg-[#0a0e14] rounded-xl p-5 border border-gray-800">
              <h3 className="text-cyan-400 font-bold text-lg mb-2 bg-cyan-950/30 inline-block px-3 py-1 rounded-md">
                {def.term}
              </h3>
              <p className="text-gray-300 leading-relaxed mb-4">
                {def.description}
              </p>
              <div className="bg-[#1a1f2e] rounded-lg p-4 border-l-4 border-indigo-500">
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

      <Modal
        isOpen={isFactorsOpen}
        onClose={() => setIsFactorsOpen(false)}
        title="Factor Library"
        maxWidth="max-w-4xl"
      >
        <div className="text-gray-400 mb-6">{activeFactorsCount} factors available</div>
        
        <div className="relative mb-6">
          <input 
            type="text" 
            placeholder="Search factors..." 
            className="w-full bg-[#0a0e14] border border-gray-700 rounded-lg py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
          />
          <svg className="absolute right-4 top-3.5 w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        <div className="space-y-3">
          {factors.map((factor, idx) => (
            <div key={idx} className="bg-[#0a0e14]/50 hover:bg-[#0a0e14] transition-colors rounded-xl p-5 border border-gray-800">
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
