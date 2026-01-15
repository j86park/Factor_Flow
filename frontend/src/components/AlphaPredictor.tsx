import { useState, useEffect } from 'react';

interface AlphaPredictorStock {
    ticker: string;
    predicted_return: number;
    percentile_rank: number;
}

interface AlphaPredictorData {
    factor_name: string;
    description: string;
    stocks: AlphaPredictorStock[];
    run_date: string | null;
}

import { API_BASE_URL } from '../config';

function formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
    });
}

function formatPercent(value: number): string {
    return `${value >= 0 ? '+' : ''}${(value * 100).toFixed(2)}%`;
}

export function AlphaPredictor() {
    const [data, setData] = useState<AlphaPredictorData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`${API_BASE_URL}/api/alpha-predictor?limit=10`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch: ${response.statusText}`);
                }
                const result = await response.json();
                setData(result);
            } catch (err) {
                console.error('Error fetching AlphaPredictor data:', err);
                setError(err instanceof Error ? err.message : 'Failed to load data');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    return (
        <div style={{ marginBottom: '80px' }} className="max-w-[96.5%] mx-auto">
            <div className="bg-gradient-to-br from-[#0e1419] via-[#12181f] to-[#0e1419] rounded-[2rem] p-8 border border-[#0a0d11] shadow-2xl">
                {/* Header */}
                <div className="flex items-center gap-4 mb-6">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center border border-purple-500/30">
                        <svg className="w-6 h-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-white">AlphaPredictor</h2>
                        <p className="text-gray-500 text-sm">GNN-Powered Weekly Return Predictions</p>
                    </div>
                </div>

                {/* Description */}
                <div className="mb-6 px-2">
                    <p className="text-gray-400 text-sm leading-relaxed">
                        {data?.description || 'The model predicts next week\'s return by combining a stock\'s own price trends with the learned influence of every other stock it correlates with in the market network.'}
                    </p>
                </div>

                {/* Loading State */}
                {loading && (
                    <div className="py-12 text-center">
                        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400 mb-4"></div>
                        <p className="text-gray-400">Loading predictions...</p>
                    </div>
                )}

                {/* Error State */}
                {error && (
                    <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-4">
                        <p className="text-red-400 text-center">Error: {error}</p>
                    </div>
                )}

                {/* Content */}
                {!loading && !error && data && data.stocks.length > 0 && (
                    <div className="bg-gradient-to-br from-[#0a0f16] via-[#0d1320] to-[#0a0f16] rounded-2xl p-6 border border-[#1a2535]">
                        {/* Section Header */}
                        <div className="flex items-center justify-between mb-4 px-2">
                            <h3 className="text-lg font-semibold text-white">Top 10 Predicted Performers</h3>
                            {data.run_date && (
                                <span className="text-gray-500 text-sm">As of {formatDate(data.run_date)}</span>
                            )}
                        </div>

                        {/* Stock Grid */}
                        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                            {data.stocks.map((stock, idx) => (
                                <div
                                    key={stock.ticker}
                                    className="bg-gradient-to-br from-[#0d1218] to-[#0a0e14] rounded-xl p-4 border border-[#1a2535] hover:border-purple-500/50 transition-all duration-200"
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-xs text-gray-500">#{idx + 1}</span>
                                        <span className="text-xs text-purple-400/80 font-medium">
                                            P{(stock.percentile_rank * 100).toFixed(0)}
                                        </span>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-lg font-bold text-white mb-1">{stock.ticker}</p>
                                        <p className={`text-sm font-semibold ${stock.predicted_return >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                            {formatPercent(stock.predicted_return)}
                                        </p>
                                        <p className="text-xs text-gray-500 mt-1">predicted</p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Disclaimer */}
                        <div className="mt-4 px-2">
                            <p className="text-gray-600 text-xs text-center">
                                * Predictions are for informational purposes only. Not investment advice.
                            </p>
                        </div>
                    </div>
                )}

                {/* Empty State */}
                {!loading && !error && data && data.stocks.length === 0 && (
                    <div className="py-12 text-center">
                        <p className="text-gray-400">No predictions available. Run the GNN Alpha Generator first.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
