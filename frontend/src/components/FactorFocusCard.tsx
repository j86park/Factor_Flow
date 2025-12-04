import { useState } from 'react';

interface FactorData {
  name: string;
  returns: {
    '1D': number | null;
    '5D': number | null;
    '1M': number | null;
  };
}

// Placeholder data structure - factors will be empty until populated
const EMPTY_FACTORS: FactorData[] = [
  { name: 'Momo Long v Short', returns: { '1D': null, '5D': null, '1M': null } },
  { name: 'HF Unwind Index', returns: { '1D': null, '5D': null, '1M': null } },
  { name: 'Valuation High v Low', returns: { '1D': null, '5D': null, '1M': null } },
  { name: 'Longs vs Shorts Crowded', returns: { '1D': null, '5D': null, '1M': null } },
  { name: 'Quality High vs Low', returns: { '1D': null, '5D': null, '1M': null } },
];

function ReturnCell({ value }: { value: number | null }) {
  if (value === null) {
    return (
      <div className="px-4 py-2 rounded-lg bg-[#1a2332] text-gray-500 text-sm font-mono text-center min-w-[80px]">
        --
      </div>
    );
  }

  const isPositive = value > 0;
  const isNegative = value < 0;
  
  let bgColor = 'bg-[#1a2332]';
  let textColor = 'text-gray-400';
  
  if (isPositive) {
    bgColor = 'bg-emerald-900/30';
    textColor = 'text-emerald-400';
  } else if (isNegative) {
    bgColor = 'bg-red-900/30';
    textColor = 'text-red-400';
  }

  const formatted = `${isPositive ? '+' : ''}${value.toFixed(2)}%`;

  return (
    <div className={`px-4 py-2 rounded-lg ${bgColor} ${textColor} text-sm font-mono text-center min-w-[80px]`}>
      {formatted}
    </div>
  );
}

export function FactorFocusCard() {
  const [factors] = useState<FactorData[]>(EMPTY_FACTORS);

  // In the future, you can add setFactors back and fetch real factor data from the backend
  // useEffect(() => {
  //   const fetchFactors = async () => {
  //     const res = await fetch('/api/factor-focus');
  //     if (res.ok) setFactors(await res.json());
  //   };
  //   fetchFactors();
  // }, []);

  return (
    <div style={{ marginTop: '20px' }} className="bg-[#1a2332] rounded-[2rem] p-8 shadow-2xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <div className="w-12 h-12 bg-yellow-500 rounded-xl flex items-center justify-center shadow-lg shadow-yellow-500/20">
          <span className="text-2xl">⭐</span>
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">Factor Focus of the Week</h2>
          <p className="text-gray-400 text-sm">Key factors to watch</p>
        </div>
      </div>

      {/* Content Card */}
      <div className="rounded-2xl p-6">
        {/* Table Header */}
        <div className="flex items-center justify-between mb-4 px-4">
          <span className="text-gray-500 text-xs font-semibold uppercase tracking-wider w-1/2">Factor</span>
          <div className="flex gap-4 w-1/2 justify-end">
            <span className="text-gray-500 text-xs font-semibold uppercase tracking-wider text-center min-w-[80px]">1D</span>
            <span className="text-gray-500 text-xs font-semibold uppercase tracking-wider text-center min-w-[80px]">5D</span>
            <span className="text-gray-500 text-xs font-semibold uppercase tracking-wider text-center min-w-[80px]">1M</span>
          </div>
        </div>

        {/* Factor Rows */}
        <div className="space-y-3">
          {factors.map((factor, idx) => (
            <div 
              key={idx} 
              className="flex items-center justify-between bg-[#151d2a] rounded-xl px-4 py-4 hover:bg-[#1a2332] transition-colors"
            >
              <span className="text-white font-medium w-1/2">{factor.name}</span>
              <div className="flex gap-4 w-1/2 justify-end">
                <ReturnCell value={factor.returns['1D']} />
                <ReturnCell value={factor.returns['5D']} />
                <ReturnCell value={factor.returns['1M']} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

