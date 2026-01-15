import { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface ZScoreDataPoint {
  date: string;
  zscore: number;
  factor_value: number | null;
}

interface ZScoreStats {
  current_zscore: number | null;
  avg_zscore: number | null;
  max_zscore: number | null;
  min_zscore: number | null;
  current_value: number | null;
}

interface ZScoreData {
  factor_id: number;
  factor_name: string;
  stats: ZScoreStats;
  history: ZScoreDataPoint[];
}

interface ZScoreModalProps {
  isOpen: boolean;
  onClose: () => void;
  factorId: number | null;
  factorName: string;
}

import { API_BASE_URL } from '../config';

function StatCard({ label, value, isPercent = false }: { label: string; value: number | null; isPercent?: boolean }) {
  const formatValue = (val: number | null): string => {
    if (val === null || val === undefined) return 'N/A';
    if (isPercent) {
      const sign = val >= 0 ? '+' : '';
      return `${sign}${(val * 100).toFixed(2)}%`;
    }
    const sign = val >= 0 ? '+' : '';
    return `${sign}${val.toFixed(3)}`;
  };

  const getColor = (val: number | null): string => {
    if (val === null) return 'text-gray-400';
    return val >= 0 ? 'text-teal-400' : 'text-orange-400';
  };

  return (
    <div className="bg-[#0a0e14] border border-gray-800 rounded-xl p-4 flex-1 min-w-[140px]">
      <div className="text-gray-400 text-xs uppercase tracking-wider mb-2">{label}</div>
      <div className={`text-2xl font-bold ${getColor(value)}`}>
        {formatValue(value)}
      </div>
    </div>
  );
}

export function ZScoreModal({ isOpen, onClose, factorId, factorName }: ZScoreModalProps) {
  // DEBUG
  console.log('ZScoreModal component - isOpen:', isOpen, 'factorId:', factorId);

  const [data, setData] = useState<ZScoreData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && factorId) {
      const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
          const response = await fetch(`${API_BASE_URL}/api/factor-zscore/${factorId}`);
          if (!response.ok) {
            throw new Error(`Failed to fetch Z-score data: ${response.statusText}`);
          }
          const result = await response.json();
          setData(result);
        } catch (err) {
          console.error('Error fetching Z-score data:', err);
          setError(err instanceof Error ? err.message : 'Failed to load data');
        } finally {
          setLoading(false);
        }
      };
      fetchData();
    }
  }, [isOpen, factorId]);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) {
    console.log('ZScoreModal: returning null because isOpen is false');
    return null;
  }

  console.log('ZScoreModal: RENDERING MODAL - isOpen is true');

  // Format chart data with shortened date labels
  const chartData = data?.history.map((point) => ({
    ...point,
    dateLabel: new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: '2-digit' }),
  })) || [];

  return (
    <div
      className="fixed inset-0 z-[9999] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
      style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 9999 }}
      onClick={onClose}
    >
      <div
        className="bg-[#0d1321] border border-gray-800/50 rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between px-8 pt-6 pb-4 border-b border-gray-800/30">
          <div>
            <h2 className="text-2xl font-bold text-white">{factorName}</h2>
            <p className="text-gray-400 text-sm mt-1">252-Day Rolling Z-Score Analysis</p>
          </div>
          <button
            onClick={onClose}
            className="bg-red-500 hover:bg-red-600 text-white p-2 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-8">
          {loading && (
            <div className="text-center py-12">
              <p className="text-gray-400">Loading Z-score data...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-4 mb-4">
              <p className="text-red-400 text-center">{error}</p>
            </div>
          )}

          {!loading && !error && data && (
            <>
              {/* Stats Row */}
              <div className="flex gap-4 mb-8 flex-wrap">
                <StatCard label="Current Z-Score" value={data.stats.current_zscore} />
                <StatCard label="Average Z-Score" value={data.stats.avg_zscore} />
                <StatCard label="Max Z-Score" value={data.stats.max_zscore} />
                <StatCard label="Min Z-Score" value={data.stats.min_zscore} />
                <StatCard label="Current Value" value={data.stats.current_value} isPercent />
              </div>

              {/* Chart */}
              {chartData.length > 0 ? (
                <div className="bg-[#080b12] rounded-xl p-6 border border-gray-800/30">
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis
                        dataKey="dateLabel"
                        stroke="#64748b"
                        tick={{ fill: '#64748b', fontSize: 11 }}
                        tickLine={{ stroke: '#64748b' }}
                        interval="preserveStartEnd"
                      />
                      <YAxis
                        stroke="#64748b"
                        tick={{ fill: '#64748b', fontSize: 11 }}
                        tickLine={{ stroke: '#64748b' }}
                        domain={[-4, 4]}
                        label={{
                          value: 'Z-Score',
                          angle: -90,
                          position: 'insideLeft',
                          fill: '#22d3ee',
                          fontSize: 12,
                        }}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#1e293b',
                          border: '1px solid #334155',
                          borderRadius: '8px',
                          color: '#f1f5f9',
                        }}
                        labelStyle={{ color: '#94a3b8' }}
                        formatter={(value) => [typeof value === 'number' ? value.toFixed(3) : '-', 'Z-Score']}
                      />
                      {/* Reference lines at +2 and -2 sigma */}
                      <ReferenceLine
                        y={2}
                        stroke="#eab308"
                        strokeDasharray="5 5"
                        label={{ value: '+2σ', fill: '#eab308', fontSize: 11, position: 'right' }}
                      />
                      <ReferenceLine y={0} stroke="#475569" strokeDasharray="3 3" />
                      <ReferenceLine
                        y={-2}
                        stroke="#eab308"
                        strokeDasharray="5 5"
                        label={{ value: '-2σ', fill: '#eab308', fontSize: 11, position: 'right' }}
                      />
                      {/* Main line */}
                      <Line
                        type="monotone"
                        dataKey="zscore"
                        stroke="#22d3ee"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4, fill: '#22d3ee' }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                  <div className="text-center mt-4">
                    <span className="text-cyan-400 text-sm">● 252-Day Rolling Z-Score</span>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 bg-[#080b12] rounded-xl border border-gray-800/30">
                  <p className="text-gray-500">No Z-score history available.</p>
                  <p className="text-gray-600 text-sm mt-2">Run calculate_zscores.py to generate data.</p>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
