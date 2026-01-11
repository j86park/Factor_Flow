interface FactorSparklineProps {
  perf_1d: number | null;
  perf_5d: number | null;
  perf_1m: number | null;
  perf_3m: number | null;
  perf_6m: number | null;
  perf_1y: number | null;
  selectedTimeframe: string;
}

const TIMEFRAME_MAP: Record<string, keyof Omit<FactorSparklineProps, 'selectedTimeframe'>> = {
  '1D': 'perf_1d',
  '5D': 'perf_5d',
  '1M': 'perf_1m',
  '3M': 'perf_3m',
  '6M': 'perf_6m',
  '12M': 'perf_1y',
};

export function FactorSparkline({
  perf_1d,
  perf_5d,
  perf_1m,
  perf_3m,
  perf_6m,
  perf_1y,
  selectedTimeframe,
}: FactorSparklineProps) {
  // Collect all performance values in order (short to long term)
  const allValues = [perf_1d, perf_5d, perf_1m, perf_3m, perf_6m, perf_1y];
  const validValues = allValues.filter((v): v is number => v !== null && v !== undefined);
  
  // Get the selected timeframe's value
  const selectedKey = TIMEFRAME_MAP[selectedTimeframe] || 'perf_1d';
  const props = { perf_1d, perf_5d, perf_1m, perf_3m, perf_6m, perf_1y };
  const selectedValue = props[selectedKey];
  
  // Check if we have any performance data
  const hasData = validValues.length > 0;
  
  if (!hasData) {
    return (
      <div className="flex items-center gap-2">
        <div className="w-16 h-8 bg-gray-800/50 rounded flex items-center justify-center">
          <span className="text-gray-500 text-xs">N/A</span>
        </div>
      </div>
    );
  }
  
  // Generate sparkline points
  const width = 64;
  const height = 24;
  const padding = 2;
  
  // Use all values for sparkline, replacing nulls with 0 for visualization
  const sparklineValues = allValues.map(v => v ?? 0);
  
  const minVal = Math.min(...sparklineValues);
  const maxVal = Math.max(...sparklineValues);
  const range = maxVal - minVal || 1; // Avoid division by zero
  
  // Calculate points for the sparkline
  const points = sparklineValues.map((val, i) => {
    const x = padding + (i / (sparklineValues.length - 1)) * (width - 2 * padding);
    const y = height - padding - ((val - minVal) / range) * (height - 2 * padding);
    return `${x},${y}`;
  }).join(' ');
  
  // Determine color based on the selected value
  const isPositive = selectedValue !== null && selectedValue >= 0;
  const lineColor = isPositive ? '#22c55e' : '#ef4444';
  const bgColor = isPositive ? 'bg-green-900/20' : 'bg-red-900/20';
  
  // Format percentage
  const formatPercent = (val: number | null): string => {
    if (val === null || val === undefined) return 'N/A';
    const sign = val >= 0 ? '+' : '';
    return `${sign}${(val * 100).toFixed(1)}%`;
  };
  
  return (
    <div className="flex items-center gap-3">
      {/* Sparkline SVG */}
      <div className={`rounded ${bgColor} p-1`}>
        <svg width={width} height={height} className="overflow-visible">
          {/* Zero line */}
          {minVal < 0 && maxVal > 0 && (
            <line
              x1={padding}
              x2={width - padding}
              y1={height - padding - ((0 - minVal) / range) * (height - 2 * padding)}
              y2={height - padding - ((0 - minVal) / range) * (height - 2 * padding)}
              stroke="#4b5563"
              strokeWidth="1"
              strokeDasharray="2,2"
            />
          )}
          {/* Sparkline */}
          <polyline
            points={points}
            fill="none"
            stroke={lineColor}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          {/* End dot */}
          {sparklineValues.length > 0 && (
            <circle
              cx={width - padding}
              cy={height - padding - ((sparklineValues[sparklineValues.length - 1] - minVal) / range) * (height - 2 * padding)}
              r="3"
              fill={lineColor}
            />
          )}
        </svg>
      </div>
      
      {/* Performance value */}
      <span
        className={`text-sm font-bold ${isPositive ? 'text-green-400' : 'text-red-400'}`}
      >
        {formatPercent(selectedValue)}
      </span>
    </div>
  );
}
