import { useState, useEffect } from 'react';
import { Target } from 'lucide-react';
import { Modal } from './Modal';
import { ZScoreModal } from './ZScoreModal';
import { FactorRotationQuadrant } from './FactorRotationQuadrant';

interface TopFactor {
  id: number;
  name: string;
  description: string;
  perf_1d: number | null;
  perf_5d: number | null;
  perf_1m: number | null;
}

import { API_BASE_URL } from '../config';

function ReturnCell({ value }: { value: number | null }) {
  if (value === null || value === undefined) {
    return (
      <div className="px-3 py-1.5 text-xs font-semibold text-center w-full" style={{ color: '#6b7280' }}>
        --
      </div>
    );
  }

  // Convert from decimal to percentage (0.05 -> 5%)
  const percentValue = value * 100;
  const isPositive = percentValue > 0;
  const isNegative = percentValue < 0;

  // Use inline styles for colors (Tailwind JIT doesn't detect dynamic classes)
  const textColor = isPositive ? '#4ade80' : isNegative ? '#f87171' : '#9ca3af';

  const formatted = `${isPositive ? '+' : ''}${percentValue.toFixed(2)}%`;

  return (
    <div className="px-3 py-1.5 text-xs font-semibold text-center w-full" style={{ color: textColor }}>
      {formatted}
    </div>
  );
}



export function FactorFocusCard() {
  const [topFactors, setTopFactors] = useState<TopFactor[]>([]);
  const [themeTitle, setThemeTitle] = useState<string>('Top Performers');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRotationOpen, setIsRotationOpen] = useState(false);
  const [selectedFactor, setSelectedFactor] = useState<TopFactor | null>(null);

  useEffect(() => {
    const fetchTopFactors = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Fetch top 5 factors by weekly performance
        const response = await fetch(`${API_BASE_URL}/api/top-factors?limit=5`);
        if (!response.ok) {
          throw new Error(`Failed to fetch top factors: ${response.statusText}`);
        }
        const factors: TopFactor[] = await response.json();
        setTopFactors(factors);

        // If we have factors, generate a theme title
        if (factors.length > 0) {
          const factorNames = factors.map(f => f.name);
          try {
            const titleResponse = await fetch(`${API_BASE_URL}/api/generate-theme-title`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ factor_names: factorNames }),
            });
            if (titleResponse.ok) {
              const titleData = await titleResponse.json();
              setThemeTitle(titleData.title);
            }
          } catch (titleError) {
            console.error('Error generating theme title:', titleError);
            // Keep default title on error
          }
        }
      } catch (err) {
        console.error('Error fetching top factors:', err);
        setError(err instanceof Error ? err.message : 'Failed to load factors');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTopFactors();
  }, []);

  // DEBUG: Log selectedFactor state on each render
  console.log('FactorFocusCard render - selectedFactor:', selectedFactor);
  console.log('ZScoreModal props:', { isOpen: selectedFactor !== null, factorId: selectedFactor?.id });

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
          {isLoading && (
            <div className="text-center py-12">
              <p className="text-gray-400">Loading top factors...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-4 mb-4">
              <p className="text-red-400 text-center">Error: {error}</p>
            </div>
          )}

          {!isLoading && !error && topFactors.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No performance data available yet.</p>
              <p className="text-gray-600 text-sm mt-2">Run the performance calculation script to populate data.</p>
            </div>
          )}

          {!isLoading && !error && topFactors.length > 0 && (
            <div className="mb-8 bg-gradient-to-br from-[#0a0f16] via-[#0d1320] to-[#0a0f16] rounded-[4rem] p-[60px]">
              <div className="px-[30px]">
                {/* Category Title - Dynamic from LLM */}
                <h3 className="text-2xl font-bold text-indigo-400 mb-[30px]">{themeTitle}</h3>

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
                <div className="space-y-[12px]">
                  {topFactors.map((factor) => (
                    <div
                      key={factor.id}
                      onClick={() => {
                        console.log('Factor clicked:', factor);
                        setSelectedFactor(factor);
                      }}
                      className="flex items-center py-[16px] px-[20px] bg-[#1a2a3d]/40 hover:bg-[#1e3045]/60 transition-colors rounded-2xl border border-[#2a3f5f]/50 cursor-pointer"
                    >
                      <span className="text-white font-medium text-base min-w-[300px]">{factor.name}</span>
                      <div className="flex gap-[18px]">
                        <div className="w-[120px]"><ReturnCell value={factor.perf_1d} /></div>
                        <div className="w-[120px]"><ReturnCell value={factor.perf_5d} /></div>
                        <div className="w-[120px]"><ReturnCell value={factor.perf_1m} /></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Factor Rotation Modal */}
      <Modal
        isOpen={isRotationOpen}
        onClose={() => setIsRotationOpen(false)}
        title="Factor Rotation Quadrant"
        subtitle="Visualize factor momentum and identify rotation opportunities"
      >
        <FactorRotationQuadrant />
      </Modal>

      {/* Z-Score Detail Modal */}
      <ZScoreModal
        isOpen={selectedFactor !== null}
        onClose={() => setSelectedFactor(null)}
        factorId={selectedFactor?.id ?? null}
        factorName={selectedFactor?.name ?? ''}
      />
    </div>
  );
}
