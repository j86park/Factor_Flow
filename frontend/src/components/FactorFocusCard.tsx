import { useState } from 'react';
import { Target } from 'lucide-react';
import { Modal } from './Modal';

interface FactorData {
  name: string;
  returns: {
    '1D': number | null;
    '5D': number | null;
    '1M': number | null;
  };
}

interface CategoryData {
  category: string;
  factors: FactorData[];
}

// Placeholder data structure - factors will be empty until populated
const EMPTY_CATEGORIES: CategoryData[] = [
  {
    category: 'AI & Momentum',
    factors: [
      { name: 'OAI Ecosystem', returns: { '1D': null, '5D': null, '1M': null } },
      { name: 'Team TPU', returns: { '1D': null, '5D': null, '1M': null } },
      { name: 'AI Private Credit', returns: { '1D': null, '5D': null, '1M': null } },
      { name: 'Momentum Long', returns: { '1D': null, '5D': null, '1M': null } },
      { name: 'Momentum Short', returns: { '1D': null, '5D': null, '1M': null } },
    ]
  }
];

function ReturnCell({ value }: { value: number | null }) {
  if (value === null) {
    return (
      <div className="px-3 py-1.5 rounded-md bg-gray-800/30 text-gray-500 text-xs font-semibold text-center w-full">
        --
      </div>
    );
  }

  const isPositive = value > 0;
  const isNegative = value < 0;
  
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

  const formatted = `${isPositive ? '+' : ''}${value.toFixed(2)}%`;

  return (
    <div className={`px-3 py-1.5 rounded-md ${bgColor} ${textColor} text-xs font-semibold text-center w-full`}>
      {formatted}
    </div>
  );
}

export function FactorFocusCard() {
  const [categories] = useState<CategoryData[]>(EMPTY_CATEGORIES);
  const [isRotationOpen, setIsRotationOpen] = useState(false);

  return (
    <div style={{ marginTop: '20px' }} className="max-w-[96.5%] mx-auto bg-gradient-to-br from-[#0e1419] via-[#12181f] to-[#0e1419] rounded-[2rem] p-8 shadow-2xl border border-[#0a0d11]">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <h2 className="text-2xl md:text-3xl font-bold text-white leading-none">
          Factor Focus of the Week
          <br />
          <span style={{ fontSize: '0.75rem', display: 'block', marginTop: '-0.25rem' }} className="text-gray-400 font-normal">Key factors to watch</span>
        </h2>
        
        {/* Factor Rotation Button */}
        <button
          onClick={() => setIsRotationOpen(true)}
          style={{ backgroundColor: '#2d2459', color: '#c4b5fd', marginTop: '12px' }}
          className="flex items-center gap-3 px-6 py-3 rounded-full hover:opacity-80 transition-all font-bold self-start"
        >
          <Target className="w-5 h-5" />
          <span>Factor Rotation</span>
        </button>
      </div>

        <div className="flex justify-center">
          <div className="w-auto">
            {categories.map((category, catIdx) => (
              <div key={catIdx} className="mb-8 bg-gradient-to-br from-[#0a0f16] via-[#0d1320] to-[#0a0f16] rounded-[4rem] p-[60px]">
                <div className="px-[30px]">
                  {/* Category Title */}
                  <h3 className="text-2xl font-bold text-indigo-400 mb-[30px]">{category.category}</h3>
                  
                  {/* Table Header */}
                  <div className="flex items-center mb-[20px]">
                    <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider min-w-[300px]">Factor</span>
                    <div className="flex gap-[18px]">
                      <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider text-center w-[120px]">1D</span>
                      <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider text-center w-[120px]">5D</span>
                      <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider text-center w-[120px]">1M</span>
                    </div>
                  </div>

                  {/* Factor Rows */}
                  <div className="space-y-[15px]">
                    {category.factors.map((factor, idx) => (
                      <div 
                        key={idx} 
                        className="flex items-center py-[15px] hover:bg-[#1a2332]/30 transition-colors rounded-lg"
                      >
                        <span className="text-white font-medium text-base min-w-[300px]">{factor.name}</span>
                        <div className="flex gap-[18px]">
                          <div className="w-[120px]"><ReturnCell value={factor.returns['1D']} /></div>
                          <div className="w-[120px]"><ReturnCell value={factor.returns['5D']} /></div>
                          <div className="w-[120px]"><ReturnCell value={factor.returns['1M']} /></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

      {/* Factor Rotation Modal */}
      <Modal
        isOpen={isRotationOpen}
        onClose={() => setIsRotationOpen(false)}
        title="Factor Rotation"
        subtitle="Analyze factor performance trends"
      >
        <div className="space-y-6">
          <p className="text-gray-300 text-center py-8">
            Factor rotation analysis content will go here...
          </p>
        </div>
      </Modal>
    </div>
  );
}

