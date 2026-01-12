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

function formatPercent(value: number | null): string {
  if (value === null || value === undefined) return '--';
  const percent = value * 100;
  const sign = percent >= 0 ? '+' : '';
  return `${sign}${percent.toFixed(2)}%`;
}

function FactorRow({ 
  rank, 
  name, 
  value, 
  isTop 
}: { 
  rank: number; 
  name: string; 
  value: number | null; 
  isTop: boolean;
}) {
  const textColor = isTop ? 'text-teal-400' : 'text-orange-400';
  const rankBg = isTop ? 'bg-teal-500/30 text-teal-300' : 'bg-orange-500/30 text-orange-300';

  return (
    <div className="flex items-center justify-between py-4 px-4 hover:bg-white/5 transition-colors rounded-lg">
      <div className="flex items-center gap-4">
        <span className={`w-8 h-8 rounded-full ${rankBg} flex items-center justify-center text-sm font-bold`}>
          {rank}
        </span>
        <span className="text-white font-medium">{name}</span>
      </div>
      <span className={`${textColor} font-bold text-lg`}>
        {formatPercent(value)}
      </span>
    </div>
  );
}

function FactorPanel({
  title,
  subtitle,
  icon,
  factors,
  timeFrame,
  isTop,
}: {
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  factors: Factor[];
  timeFrame: TimeFrame;
  isTop: boolean;
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
    <div className="flex-1 bg-gradient-to-br from-[#0e1419] via-[#12181f] to-[#0e1419] rounded-[2rem] p-8 border border-[#0a0d11] shadow-2xl min-h-[400px]">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        {icon}
        <div>
          <h3 className="text-xl font-bold text-white">{title}</h3>
          <p className="text-gray-500 text-sm">{subtitle}</p>
        </div>
      </div>

      {/* Factor List */}
      <div className="space-y-2">
        {factors.map((factor, index) => (
          <FactorRow
            key={factor.id}
            rank={index + 1}
            name={factor.name}
            value={getPerformance(factor)}
            isTop={isTop}
          />
        ))}
        {factors.length === 0 && (
          <p className="text-gray-500 text-center py-8">No data available</p>
        )}
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
    <div style={{ marginTop: '20px' }} className="max-w-[96.5%] mx-auto">
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
        <div className="flex gap-6">
          <FactorPanel
            title="Top Factors"
            subtitle="Strongest momentum"
            icon={<Flame className="w-8 h-8 text-orange-400" />}
            factors={topFactors}
            timeFrame={timeFrame as TimeFrame}
            isTop={true}
          />
          <FactorPanel
            title="Bottom Factors"
            subtitle="Under pressure"
            icon={<TrendingDown className="w-8 h-8 text-red-400" />}
            factors={bottomFactors}
            timeFrame={timeFrame as TimeFrame}
            isTop={false}
          />
        </div>
      )}
    </div>
  );
}
