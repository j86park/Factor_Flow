import { useState, useEffect } from 'react';

interface MarketAnalysis {
    date: string;
    analysis: string;
}

const API_BASE_URL = 'http://localhost:8000';

function formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
    });
}

export function DailyFactorSummary() {
    const [analysis, setAnalysis] = useState<MarketAnalysis | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchAnalysis = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`${API_BASE_URL}/api/market-analysis`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch analysis: ${response.statusText}`);
                }
                const data = await response.json();
                setAnalysis(data);
            } catch (err) {
                console.error('Error fetching market analysis:', err);
                setError(err instanceof Error ? err.message : 'Failed to load analysis');
            } finally {
                setLoading(false);
            }
        };

        fetchAnalysis();
    }, []);

    // Parse analysis into paragraphs
    const paragraphs = analysis?.analysis.split('\n\n').filter(p => p.trim()) || [];

    return (
        <div style={{ marginBottom: '80px' }} className="max-w-[96.5%] mx-auto">
            <div className="bg-gradient-to-br from-[#0e1419] via-[#12181f] to-[#0e1419] rounded-[2rem] p-8 border border-[#0a0d11] shadow-2xl">
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <div>
                        <h2 className="text-xl font-bold text-white">Daily Factor Summary</h2>
                        <p className="text-gray-500 text-sm">AI Generated Data Synthesis (BETA testing — not investment advice)</p>
                    </div>
                </div>

                {/* Loading State */}
                {loading && (
                    <div className="py-12 text-center">
                        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mb-4"></div>
                        <p className="text-gray-400">Generating market analysis...</p>
                    </div>
                )}

                {/* Error State */}
                {error && (
                    <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-4">
                        <p className="text-red-400 text-center">Error: {error}</p>
                    </div>
                )}

                {/* Content */}
                {!loading && !error && analysis && (
                    <div className="flex justify-center">
                        <div className="w-auto min-w-[70%] max-w-[92%]">
                            <div className="bg-gradient-to-br from-[#0a0f16] via-[#0d1320] to-[#0a0f16] rounded-[2rem] p-10 border border-[#1a2535]">
                                {/* Section Header */}
                                <div className="flex items-start justify-between mb-6 px-4">
                                    <h3 className="text-lg font-semibold text-white">Market Summary - Close</h3>
                                    <span className="text-gray-500 text-sm">{formatDate(analysis.date)}</span>
                                </div>

                                {/* Analysis Paragraphs */}
                                <div className="space-y-4 px-4">
                                    {paragraphs.map((paragraph, idx) => (
                                        <p key={idx} className="text-gray-300 text-sm leading-relaxed">
                                            {paragraph}
                                        </p>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
