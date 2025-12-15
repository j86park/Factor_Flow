import { useState, useEffect } from 'react';
import { BarChart3 } from 'lucide-react';
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

// API endpoint - adjust if your backend runs on a different port
const API_BASE_URL = 'http://localhost:8000';

// Mock factors data
const MOCK_FACTORS: Factor[] = [
  {
    name: 'Agg',
    description: 'Agricultural commodities and farming equipment. Food security and weather-dependent.',
    category: 'Sector'
  },
  {
    name: 'AI Adopters Early',
    description: 'Companies deploying AI to improve margins and productivity. Efficiency gains from AI tools.',
    category: 'Theme'
  },
  {
    name: 'AI Private Credit',
    description: 'Private credit funds focused on AI-related investments. Exposure to private debt financing in the AI sector.',
    category: 'Theme'
  }
];

export function DashboardControls() {
  const [selectedTimeFrame, setSelectedTimeFrame] = useState('1D');
  const [isDefinitionsOpen, setIsDefinitionsOpen] = useState(false);
  const [isFactorsOpen, setIsFactorsOpen] = useState(false);
  
  const [definitions, setDefinitions] = useState<Definition[]>([]);
  const [factors] = useState<Factor[]>(MOCK_FACTORS);
  const [currentDate, setCurrentDate] = useState('');
  const [definitionsLoading, setDefinitionsLoading] = useState(false);
  const [definitionsError, setDefinitionsError] = useState<string | null>(null);

  // The active factors count is now dynamically based on the fetched factors
  const activeFactorsCount = factors.length;

  // Helper function to get the last market day (weekday)
  const getLastMarketDay = (): string => {
    const now = new Date();
    const day = now.getDay(); // 0 = Sunday, 6 = Saturday
    
    let daysToSubtract = 0;
    if (day === 0) {
      // Sunday - go back 2 days to Friday
      daysToSubtract = 2;
    } else if (day === 6) {
      // Saturday - go back 1 day to Friday
      daysToSubtract = 1;
    }
    
    if (daysToSubtract > 0) {
      now.setDate(now.getDate() - daysToSubtract);
    }
    
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const dayOfMonth = String(now.getDate()).padStart(2, '0');
    
    return `${year}-${month}-${dayOfMonth}`;
  };

  useEffect(() => {
    setCurrentDate(getLastMarketDay());

    const interval = setInterval(() => {
      const newDate = getLastMarketDay();
      setCurrentDate(prev => newDate !== prev ? newDate : prev);
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  // Fetch definitions from Supabase via backend API
  useEffect(() => {
    const fetchDefinitions = async () => {
      setDefinitionsLoading(true);
      setDefinitionsError(null);
      try {
        const response = await fetch(`${API_BASE_URL}/api/definitions`);
        if (!response.ok) {
          throw new Error(`Failed to fetch definitions: ${response.statusText}`);
        }
        const data = await response.json();
        setDefinitions(data);
      } catch (error) {
        console.error('Error fetching definitions:', error);
        const errorMsg = error instanceof Error ? error.message : 'Failed to load definitions';
        setDefinitionsError(`${errorMsg}. Check that backend is running on ${API_BASE_URL}`);
      } finally {
        setDefinitionsLoading(false);
      }
    };

    fetchDefinitions();
  }, []);

  return (
    <div className="w-full" style={{ marginTop: '20px' }}>
      {/* Dashboard Card Container */}
      <div className="max-w-[96.5%] mx-auto bg-gradient-to-br from-[#0e1419] via-[#12181f] to-[#0e1419] rounded-[2rem] p-10 md:p-14 shadow-2xl border border-[#0a0d11]">
        
        {/* Title Row - Centered */}
        <div className="flex items-center justify-center gap-4 mb-10">
          <BarChart3 className="w-10 h-10 md:w-12 md:h-12 text-cyan-400" />
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-light text-gray-200 tracking-tight">
            Analytics Dashboard
          </h1>
        </div>

        {/* Controls Row - Evenly spread horizontally */}
        <div className="flex flex-wrap items-center justify-center gap-[3rem] px-2">
          {/* Definitions Button - Purple tint */}
          <button 
            onClick={() => setIsDefinitionsOpen(true)}
            style={{ backgroundColor: '#2d2459', color: '#c4b5fd', height: '35px' }}
            className="flex items-center gap-3 px-6 rounded-full hover:opacity-80 transition-all text-base font-bold"
          >
            <span className="text-lg">📚</span>
            <span>Definitions</span>
          </button>

          {/* Live Feed + Date combined - Cyan for digital/real-time feel */}
          <div style={{ height: '35px' }} className="flex items-center gap-4 text-cyan-400 text-base font-bold">
            <div 
              style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: '#22c55e',
                animation: 'pulse 1.5s ease-in-out infinite',
                boxShadow: '0 0 8px #22c55e',
                flexShrink: 0
              }}
            ></div>
            <span>Live Feed <span className="text-cyan-300">As of {currentDate}</span></span>
          </div>

          {/* Active Factors - Purple tint */}
          <button 
            onClick={() => setIsFactorsOpen(true)}
            style={{ backgroundColor: '#2d2459', color: '#c4b5fd', height: '35px' }}
            className="px-6 rounded-full hover:opacity-80 transition-all text-base font-bold flex items-center"
          >
            {activeFactorsCount} Active Factors
          </button>

          {/* Time Frame Switcher - Cyan active, dark inactive */}
          <div className="flex gap-4">
            {TIME_FRAMES.map((tf) => (
              <button
                key={tf}
                onClick={() => setSelectedTimeFrame(tf)}
                style={
                  selectedTimeFrame === tf 
                    ? { backgroundColor: '#22d3ee', color: '#000000', width: '54px', height: '35px' } 
                    : { backgroundColor: '#1e2a3a', color: '#d1d5db', width: '54px', height: '35px' }
                }
                className="rounded-full text-lg font-bold transition-all duration-200 hover:opacity-80 flex items-center justify-center"
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
        subtitle="Key concepts and metrics explained"
      >
        <div className="space-y-6">
          {definitionsLoading && (
            <p className="text-center text-gray-400 py-8">Loading definitions...</p>
          )}
          {definitionsError && (
            <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-4">
              <p className="text-red-400 text-center">Error: {definitionsError}</p>
            </div>
          )}
          {!definitionsLoading && !definitionsError && definitions.map((def, idx) => (
            <div key={idx} className="bg-[#151d2a] rounded-2xl p-6 border border-gray-800/30">
              <h3 className="text-cyan-400 font-bold text-lg mb-3 bg-cyan-900/40 inline-block px-4 py-1.5 rounded-lg">
                {def.term}
              </h3>
              <p className="text-gray-300 leading-relaxed mb-5 text-base">
                {def.description}
              </p>
              {def.example && (
                <div className="bg-[#1a2640] rounded-xl p-5 border-l-4 border-blue-500">
                  <div className="flex items-start gap-3">
                    <span className="text-yellow-400 text-lg mt-0.5">💡</span>
                    <div>
                      <span className="text-blue-400 text-xs font-bold uppercase tracking-wider block mb-2">Example</span>
                      <p className="text-sm text-gray-400 leading-relaxed">{def.example}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
          {!definitionsLoading && !definitionsError && definitions.length === 0 && (
            <p className="text-center text-gray-500 py-8">No definitions loaded.</p>
          )}
        </div>
      </Modal>

      <Modal
        isOpen={isFactorsOpen}
        onClose={() => setIsFactorsOpen(false)}
        title="Factor Library"
        subtitle={`${activeFactorsCount} factors available`}
      >
        {/* Search Bar */}
        <div className="relative mb-6">
          <input 
            type="text" 
            placeholder="Search factors..." 
            className="w-full bg-[#0a0e14] border border-gray-700 rounded-xl py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
          />
        </div>

        {/* Factor List */}
        <div className="space-y-3">
          {factors.map((factor, idx) => (
            <div key={idx} className="bg-[#0a0e14]/50 hover:bg-[#0a0e14] transition-colors rounded-xl p-5 border border-gray-800">
              <h3 className="text-cyan-400 font-bold text-xl mb-2">
                {factor.name}
              </h3>
              <p className="text-gray-400 text-sm">
                {factor.description}
              </p>
            </div>
          ))}
          {factors.length === 0 && (
            <p className="text-center text-gray-500 py-8">No factors loaded.</p>
          )}
        </div>
      </Modal>
    </div>
  );
}
