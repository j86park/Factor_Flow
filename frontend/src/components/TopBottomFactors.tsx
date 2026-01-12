import { useState, useEffect } from 'react';
import { Flame, TrendingDown } from 'lucide-react';

interface Factor {
  id: number;
  name: string;
  perf_1d: number | null;
  perf_5d: number | null;
  perf_1m: number | null;
  perf_3m: number | null;
  perf_6m: number | null;
  perf_1y: number | null;
}

type TimeFrame = '1D' | '5D' | '1M' | '3M' | '6M' | '12M';

interface TopBottomFactorsProps {
  timeFrame: string;
}

const API_BASE_URL = 'http://localhost:8000';

function ReturnCell({ value }: { value: number | null }) {
  if (value === null || value === undefined) {
    return (
      <div className="px-3 py-1.5 rounded-md bg-gray-800/30 text-gray-500 text-xs font-semibold text-center w-[120px]">
        --
      </div>
    );
  }

  const percentValue = value * 100;
  const isPositive = percentValue > 0;
  const isNegative = percentValue < 0;
  
  let bgColor = '';
  let textColor = '';
  
  if (isPositive) {
    bgColor = 'bg-teal-600/80';
    textColor = 'text-white';
  } else if (isNegative) {
    bgColor = 'bg-orange-600/80';
    textColor = 'text-white';
  } else {
    bgColor = 'bg-gray-700/50';
    textColor = 'text-gray-300';
  }

  const formatted = `${isPositive ? '+' : ''}${percentValue.toFixed(2)}%`;

  return (
    <div className={`px-3 py-1.5 rounded-md ${bgColor} ${textColor} text-xs font-semibold text-center w-[120px]`}>
      {formatted}
    </div>
  );
}

function FactorRow({ 
  name, 
  value, 
}: { 
  name: string; 
  value: number | null; 
}) {
  return (
    <div className="flex items-center py-[16px] px-[20px] bg-[#1a2a3d]/40 hover:bg-[#1e3045]/60 transition-colors rounded-2xl border border-[#2a3f5f]/50">
      <span className="text-white font-medium text-base min-w-[300px]">{name}</span>
      <ReturnCell value={value} />
    </div>
  );
}

function FactorPanel({
  title,
  subtitle,
  icon,
  factors,
  timeFrame,
}: {
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  factors: Factor[];
  timeFrame: TimeFrame;
}) {
  const getPerformance = (factor: Factor): number | null => {
    switch (timeFrame) {
      case '1D': return factor.perf_1d;
      case '5D': return factor.perf_5d;
      case '1M': return factor.perf_1m;
      case '3M': return factor.perf_3m;
      case '6M': return factor.perf_6m;
      case '12M': return factor.perf_1y;
      default: return factor.perf_1d;
    }
  };

  return (
    <div className="flex-1 bg-gradient-to-br from-[#0e1419] via-[#12181f] to-[#0e1419] rounded-[1.6rem] p-6 border border-[#0a0d11] shadow-2xl min-h-[320px]">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-center gap-3">
          <h3 className="text-[1.625rem] font-bold text-white leading-none">{title}</h3>
          {icon}
        </div>
        <p className="text-gray-500 text-sm -mt-1 text-center">{subtitle}</p>
      </div>

      {/* Inner Container with darker background */}
      <div className="bg-gradient-to-br from-[#0a0f16] via-[#0d1320] to-[#0a0f16] rounded-[1.6rem] p-6 pb-10">
        {/* Table Header */}
        <div className="flex items-center mb-[20px] px-[20px]">
          <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider min-w-[300px]">Factor</span>
          <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider text-center w-[120px]">{timeFrame}</span>
        </div>

        {/* Factor List */}
        <div className="space-y-[12px]">
          {factors.map((factor) => (
            <FactorRow
              key={factor.id}
              name={factor.name}
              value={getPerformance(factor)}
            />
          ))}
          {factors.length === 0 && (
            <p className="text-gray-500 text-center py-8">No data available</p>
          )}
        </div>
      </div>
    </div>
  );
}

export function TopBottomFactors({ timeFrame }: TopBottomFactorsProps) {
  const [factors, setFactors] = useState<Factor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFactors = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${API_BASE_URL}/api/factors-with-performance`);
        if (!response.ok) {
          throw new Error(`Failed to fetch factors: ${response.statusText}`);
        }
        const data = await response.json();
        setFactors(data);
      } catch (err) {
        console.error('Error fetching factors:', err);
        setError(err instanceof Error ? err.message : 'Failed to load factors');
      } finally {
        setLoading(false);
      }
    };

    fetchFactors();
  }, []);

  const getPerformance = (factor: Factor): number | null => {
    switch (timeFrame) {
      case '1D': return factor.perf_1d;
      case '5D': return factor.perf_5d;
      case '1M': return factor.perf_1m;
      case '3M': return factor.perf_3m;
      case '6M': return factor.perf_6m;
      case '12M': return factor.perf_1y;
      default: return factor.perf_1d;
    }
  };

  // Sort and get top/bottom 5
  const sortedFactors = [...factors].sort((a, b) => {
    const aPerf = getPerformance(a) ?? -Infinity;
    const bPerf = getPerformance(b) ?? -Infinity;
    return bPerf - aPerf; // Descending
  });

  const topFactors = sortedFactors.slice(0, 5);
  const bottomFactors = sortedFactors.slice(-5).reverse(); // Reverse to show worst first

  return (
    <div style={{ marginTop: '20px', marginBottom: '80px' }} className="max-w-[96.5%] mx-auto">
      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <p className="text-gray-400">Loading factors...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-4 mb-4">
          <p className="text-red-400 text-center">Error: {error}</p>
        </div>
      )}

      {/* Panels */}
      {!loading && !error && (
        <div className="bg-gradient-to-br from-[#0e1419] via-[#12181f] to-[#0e1419] rounded-[2rem] p-6 border border-[#0a0d11] shadow-2xl">
          <div className="flex gap-8">
            <FactorPanel
              title="Top Factors"
              subtitle="Strongest momentum"
              icon={<Flame className="w-8 h-8 text-orange-400" />}
              factors={topFactors}
              timeFrame={timeFrame as TimeFrame}
            />
            <FactorPanel
              title="Bottom Factors"
              subtitle="Under pressure"
              icon={<TrendingDown className="w-8 h-8 text-red-400" />}
              factors={bottomFactors}
              timeFrame={timeFrame as TimeFrame}
            />
          </div>
        </div>
      )}
    </div>
  );
}
