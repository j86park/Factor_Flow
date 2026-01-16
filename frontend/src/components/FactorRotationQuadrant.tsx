import { useState, useEffect, useMemo } from 'react';
import {
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ReferenceLine,
    ResponsiveContainer,
    Cell,
} from 'recharts';
import { Rocket, TrendingDown, RefreshCw, AlertTriangle } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface Factor {
    id: number;
    name: string;
    description: string;
    type: string | null;
    perf_1d: number | null;
    perf_5d: number | null;
    perf_1m: number | null;
    perf_3m: number | null;
    perf_6m: number | null;
    perf_1y: number | null;
    num_holdings: number | null;
    quadrant_category: string | null;
    rotation_magnitude: number | null;
}

type ShortTermPeriod = '1D' | '5D' | '1M';
type MediumTermPeriod = '1M' | '3M' | '6M' | '12M';

interface ScatterPoint {
    name: string;
    x: number;
    y: number;
    quadrant: 'Leaders' | 'Fading' | 'Recovering' | 'Laggards';
    magnitude: number;
}

const SHORT_TERM_OPTIONS: { label: string; value: ShortTermPeriod }[] = [
    { label: '1D', value: '1D' },
    { label: '5D', value: '5D' },
    { label: '1M', value: '1M' },
];

const MEDIUM_TERM_OPTIONS: { label: string; value: MediumTermPeriod }[] = [
    { label: '1M', value: '1M' },
    { label: '3M', value: '3M' },
    { label: '6M', value: '6M' },
    { label: '12M', value: '12M' },
];

const QUADRANT_COLORS: Record<string, string> = {
    Leaders: '#22c55e',    // Green
    Fading: '#f97316',     // Orange
    Recovering: '#3b82f6', // Blue
    Laggards: '#ef4444',   // Red
};

const QUADRANT_ICONS: Record<string, React.ReactNode> = {
    Leaders: <Rocket className="w-4 h-4" />,
    Fading: <TrendingDown className="w-4 h-4" />,
    Recovering: <RefreshCw className="w-4 h-4" />,
    Laggards: <AlertTriangle className="w-4 h-4" />,
};

function getPerformanceValue(factor: Factor, period: ShortTermPeriod | MediumTermPeriod): number | null {
    switch (period) {
        case '1D': return factor.perf_1d;
        case '5D': return factor.perf_5d;
        case '1M': return factor.perf_1m;
        case '3M': return factor.perf_3m;
        case '6M': return factor.perf_6m;
        case '12M': return factor.perf_1y;
        default: return null;
    }
}

function classifyQuadrant(x: number, y: number): 'Leaders' | 'Fading' | 'Recovering' | 'Laggards' {
    if (x >= 0 && y >= 0) return 'Leaders';
    if (x < 0 && y >= 0) return 'Fading';
    if (x >= 0 && y < 0) return 'Recovering';
    return 'Laggards';
}

function formatPercent(value: number | null): string {
    if (value === null || value === undefined) return '--';
    const pct = value * 100;
    return `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%`;
}

interface CustomTooltipProps {
    active?: boolean;
    payload?: Array<{ payload: ScatterPoint }>;
    xLabel: string;
    yLabel: string;
}

function CustomTooltip({ active, payload, xLabel, yLabel }: CustomTooltipProps) {
    if (!active || !payload || payload.length === 0) return null;

    const data = payload[0].payload;

    return (
        <div className="bg-[#1a2332] border border-gray-700 rounded-lg px-4 py-3 shadow-xl">
            <p className="text-white font-semibold mb-2">{data.name}</p>
            <div className="space-y-1 text-sm">
                <p className="text-gray-400">
                    {xLabel}: <span className={data.x >= 0 ? 'text-green-400' : 'text-red-400'}>{formatPercent(data.x)}</span>
                </p>
                <p className="text-gray-400">
                    {yLabel}: <span className={data.y >= 0 ? 'text-green-400' : 'text-red-400'}>{formatPercent(data.y)}</span>
                </p>
            </div>
        </div>
    );
}

interface QuadrantCardProps {
    title: string;
    factors: ScatterPoint[];
    color: string;
    icon: React.ReactNode;
}

function QuadrantCard({ title, factors, color, icon }: QuadrantCardProps) {
    // Sort by magnitude descending
    const sorted = [...factors].sort((a, b) => b.magnitude - a.magnitude);

    return (
        <div className="bg-[#0d1321] border border-gray-800/50 rounded-xl p-4 flex-1 min-w-[200px]">
            <div className="flex items-center gap-2 mb-3">
                <span style={{ color }}>{icon}</span>
                <h4 className="font-semibold" style={{ color }}>{title}</h4>
            </div>
            <div className="space-y-1 max-h-[120px] overflow-y-auto custom-scrollbar">
                {sorted.length === 0 ? (
                    <p className="text-gray-500 text-sm">No factors</p>
                ) : (
                    sorted.map((f) => (
                        <p key={f.name} className="text-gray-300 text-sm truncate">{f.name}</p>
                    ))
                )}
            </div>
        </div>
    );
}

export function FactorRotationQuadrant() {
    const [factors, setFactors] = useState<Factor[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [xAxis, setXAxis] = useState<ShortTermPeriod>('5D');
    const [yAxis, setYAxis] = useState<MediumTermPeriod>('1M');

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

    // Calculate scatter points based on selected axes
    const scatterData = useMemo<ScatterPoint[]>(() => {
        return factors
            .map((factor) => {
                const xVal = getPerformanceValue(factor, xAxis);
                const yVal = getPerformanceValue(factor, yAxis);

                if (xVal === null || yVal === null) return null;

                return {
                    name: factor.name,
                    x: xVal,
                    y: yVal,
                    quadrant: classifyQuadrant(xVal, yVal),
                    magnitude: Math.abs(xVal) + Math.abs(yVal),
                };
            })
            .filter((p): p is ScatterPoint => p !== null);
    }, [factors, xAxis, yAxis]);

    // Calculate symmetric axis domain
    const axisDomain = useMemo(() => {
        if (scatterData.length === 0) return [-0.1, 0.1];

        const maxAbsX = Math.max(...scatterData.map((p) => Math.abs(p.x)));
        const maxAbsY = Math.max(...scatterData.map((p) => Math.abs(p.y)));
        const maxAbs = Math.max(maxAbsX, maxAbsY, 0.01) * 1.1; // Add 10% padding

        return [-maxAbs, maxAbs];
    }, [scatterData]);

    // Count by quadrant
    const quadrantCounts = useMemo(() => {
        const counts = { Leaders: 0, Fading: 0, Recovering: 0, Laggards: 0 };
        scatterData.forEach((p) => counts[p.quadrant]++);
        return counts;
    }, [scatterData]);

    // Group factors by quadrant for cards
    const quadrantGroups = useMemo(() => {
        const groups: Record<string, ScatterPoint[]> = {
            Leaders: [],
            Fading: [],
            Recovering: [],
            Laggards: [],
        };
        scatterData.forEach((p) => groups[p.quadrant].push(p));
        return groups;
    }, [scatterData]);

    const xLabel = `${xAxis} Return (%)`;
    const yLabel = `${yAxis} Return (%)`;

    return (
        <div>
            {/* Controls */}
            <div className="pb-5 flex flex-wrap items-center gap-8">
                {/* X-Axis Selector */}
                <div className="flex items-center gap-3">
                    <span className="text-gray-400 text-sm font-medium">X-Axis (Short-term):</span>
                    <div className="flex bg-[#0d1117] rounded-full p-1 border border-gray-700/50 gap-1">
                        {SHORT_TERM_OPTIONS.map((opt) => (
                            <button
                                key={opt.value}
                                onClick={() => setXAxis(opt.value)}
                                className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200 ${xAxis === opt.value
                                    ? 'border border-blue-500 text-blue-400'
                                    : 'border border-transparent text-gray-500 hover:text-gray-300'
                                    }`}
                            >
                                {opt.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Y-Axis Selector */}
                <div className="flex items-center gap-3">
                    <span className="text-gray-400 text-sm font-medium">Y-Axis (Medium-term):</span>
                    <div className="flex bg-[#0d1117] rounded-full p-1 border border-gray-700/50 gap-1">
                        {MEDIUM_TERM_OPTIONS.map((opt) => (
                            <button
                                key={opt.value}
                                onClick={() => setYAxis(opt.value)}
                                className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200 ${yAxis === opt.value
                                    ? 'border border-blue-500 text-blue-400'
                                    : 'border border-transparent text-gray-500 hover:text-gray-300'
                                    }`}
                            >
                                {opt.label}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Summary Badges */}
            <div className="pb-4 flex flex-wrap gap-3">
                {(['Leaders', 'Fading', 'Recovering', 'Laggards'] as const).map((quadrant) => (
                    <div
                        key={quadrant}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg border"
                        style={{
                            borderColor: QUADRANT_COLORS[quadrant],
                            backgroundColor: `${QUADRANT_COLORS[quadrant]}10`,
                        }}
                    >
                        <span style={{ color: QUADRANT_COLORS[quadrant] }}>{QUADRANT_ICONS[quadrant]}</span>
                        <span style={{ color: QUADRANT_COLORS[quadrant] }} className="font-medium">
                            {quadrant}: {quadrantCounts[quadrant]}
                        </span>
                    </div>
                ))}
            </div>

            {/* Chart Area */}
            <div className="pb-4">
                {loading && (
                    <div className="h-[400px] flex items-center justify-center">
                        <p className="text-gray-400">Loading factor data...</p>
                    </div>
                )}

                {error && (
                    <div className="h-[400px] flex items-center justify-center">
                        <p className="text-red-400">Error: {error}</p>
                    </div>
                )}

                {!loading && !error && (
                    <div className="relative h-[450px]">
                        {/* Quadrant Labels */}
                        <div className="absolute text-[#f9731640] font-bold text-lg z-0" style={{ top: '20%', left: '15%' }}>
                            FADING
                        </div>
                        <div className="absolute text-[#22c55e40] font-bold text-lg z-0" style={{ top: '20%', right: '15%' }}>
                            LEADERS
                        </div>
                        <div className="absolute text-[#ef444440] font-bold text-lg z-0" style={{ bottom: '25%', left: '15%' }}>
                            LAGGARDS
                        </div>
                        <div className="absolute text-[#3b82f640] font-bold text-lg z-0" style={{ bottom: '25%', right: '15%' }}>
                            RECOVERING
                        </div>

                        <ResponsiveContainer width="100%" height="100%">
                            <ScatterChart margin={{ top: 20, right: 40, bottom: 50, left: 50 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#2a3f5f40" />
                                <XAxis
                                    type="number"
                                    dataKey="x"
                                    domain={axisDomain}
                                    name={xLabel}
                                    tick={{ fill: '#9ca3af', fontSize: 12 }}
                                    tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
                                    axisLine={{ stroke: '#4b5563' }}
                                    tickLine={{ stroke: '#4b5563' }}
                                    label={{ value: xLabel, position: 'bottom', fill: '#9ca3af', fontSize: 12, dy: 10 }}
                                />
                                <YAxis
                                    type="number"
                                    dataKey="y"
                                    domain={axisDomain}
                                    name={yLabel}
                                    tick={{ fill: '#9ca3af', fontSize: 12 }}
                                    tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
                                    axisLine={{ stroke: '#4b5563' }}
                                    tickLine={{ stroke: '#4b5563' }}
                                    label={{ value: yLabel, angle: -90, position: 'left', fill: '#9ca3af', fontSize: 12, dx: -10 }}
                                />
                                <ReferenceLine x={0} stroke="#6b7280" strokeDasharray="3 3" />
                                <ReferenceLine y={0} stroke="#6b7280" strokeDasharray="3 3" />
                                <Tooltip content={<CustomTooltip xLabel={xLabel} yLabel={yLabel} />} />
                                <Scatter data={scatterData} fill="#8884d8">
                                    {scatterData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={QUADRANT_COLORS[entry.quadrant]} />
                                    ))}
                                </Scatter>
                            </ScatterChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </div>

            {/* Quadrant Cards */}
            {!loading && !error && (
                <div className="px-6 pb-6 flex gap-4 flex-wrap">
                    <QuadrantCard
                        title="Leaders"
                        factors={quadrantGroups.Leaders}
                        color={QUADRANT_COLORS.Leaders}
                        icon={QUADRANT_ICONS.Leaders}
                    />
                    <QuadrantCard
                        title="Fading"
                        factors={quadrantGroups.Fading}
                        color={QUADRANT_COLORS.Fading}
                        icon={QUADRANT_ICONS.Fading}
                    />
                    <QuadrantCard
                        title="Recovering"
                        factors={quadrantGroups.Recovering}
                        color={QUADRANT_COLORS.Recovering}
                        icon={QUADRANT_ICONS.Recovering}
                    />
                    <QuadrantCard
                        title="Laggards"
                        factors={quadrantGroups.Laggards}
                        color={QUADRANT_COLORS.Laggards}
                        icon={QUADRANT_ICONS.Laggards}
                    />
                </div>
            )}
        </div>
    );
}
