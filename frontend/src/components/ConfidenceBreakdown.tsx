interface ConfidenceBreakdownProps {
    overall: number;
    factors: Array<{
        name: string;
        confidence: number;
        source: string;
        weight: number;
    }>;
    showDetails?: boolean;
}

/**
 * ConfidenceBreakdown Component
 * 
 * Visualizes how the overall confidence score is derived
 * from individual factor confidences.
 */
export function ConfidenceBreakdown({
    overall,
    factors,
    showDetails = true
}: ConfidenceBreakdownProps) {
    const getConfidenceColor = (confidence: number) => {
        if (confidence >= 80) return 'bg-green-500';
        if (confidence >= 60) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    const getConfidenceTextColor = (confidence: number) => {
        if (confidence >= 80) return 'text-green-400';
        if (confidence >= 60) return 'text-yellow-400';
        return 'text-red-400';
    };

    const getSourceIcon = (source: string) => {
        if (source.includes('verified') || source.includes('api')) return '✓';
        if (source.includes('stated') || source.includes('user')) return '👤';
        if (source.includes('estimated')) return '~';
        return '•';
    };

    const sortedFactors = [...factors].sort((a, b) => b.weight - a.weight);

    return (
        <div className="glass rounded-xl p-6">
            {/* Overall Score */}
            <div className="text-center mb-6">
                <div className="relative inline-flex items-center justify-center">
                    <svg className="w-32 h-32 transform -rotate-90">
                        <circle
                            cx="64"
                            cy="64"
                            r="56"
                            stroke="currentColor"
                            strokeWidth="8"
                            fill="none"
                            className="text-white/10"
                        />
                        <circle
                            cx="64"
                            cy="64"
                            r="56"
                            stroke="currentColor"
                            strokeWidth="8"
                            fill="none"
                            strokeDasharray={`${overall * 3.52} 352`}
                            className={getConfidenceTextColor(overall)}
                        />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className={`text-3xl font-bold ${getConfidenceTextColor(overall)}`}>
                            {overall}%
                        </span>
                        <span className="text-white/50 text-sm">Overall</span>
                    </div>
                </div>
                <p className="text-white/60 mt-2">
                    {overall >= 80 ? 'High confidence in this assessment' :
                        overall >= 60 ? 'Moderate confidence - some factors uncertain' :
                            'Lower confidence - additional verification recommended'}
                </p>
            </div>

            {/* Factor Breakdown */}
            {showDetails && (
                <div className="space-y-4">
                    <h3 className="text-white/80 font-medium">Contributing Factors</h3>
                    {sortedFactors.map((factor, i) => (
                        <div key={i} className="bg-white/5 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-2">
                                    <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs ${factor.confidence >= 80 ? 'bg-green-500/20 text-green-400' :
                                            factor.confidence >= 60 ? 'bg-yellow-500/20 text-yellow-400' :
                                                'bg-red-500/20 text-red-400'
                                        }`}>
                                        {getSourceIcon(factor.source)}
                                    </span>
                                    <span className="text-white/80">{factor.name}</span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <span className="text-white/40 text-xs">
                                        {(factor.weight * 100).toFixed(0)}% weight
                                    </span>
                                    <span className={`font-medium ${getConfidenceTextColor(factor.confidence)}`}>
                                        {factor.confidence}%
                                    </span>
                                </div>
                            </div>
                            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                <div
                                    className={`h-full rounded-full transition-all ${getConfidenceColor(factor.confidence)}`}
                                    style={{ width: `${factor.confidence}%` }}
                                />
                            </div>
                            <p className="text-white/40 text-xs mt-1">
                                Source: {factor.source}
                            </p>
                        </div>
                    ))}
                </div>
            )}

            {/* Legend */}
            <div className="flex justify-center gap-6 mt-6 pt-4 border-t border-white/10">
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                    <span className="text-white/50 text-xs">80%+ Verified</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                    <span className="text-white/50 text-xs">60-79% Moderate</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <span className="text-white/50 text-xs">&lt;60% Low</span>
                </div>
            </div>
        </div>
    );
}

/**
 * ConfidenceMini Component
 * 
 * Compact confidence indicator for inline use.
 */
export function ConfidenceMini({ confidence }: { confidence: number }) {
    const getColor = (conf: number) => {
        if (conf >= 80) return 'text-green-400';
        if (conf >= 60) return 'text-yellow-400';
        return 'text-red-400';
    };

    return (
        <span
            className={`inline-flex items-center gap-1 ${getColor(confidence)}`}
            title={`Confidence: ${confidence}%`}
        >
            <span className="w-2 h-2 rounded-full bg-current" />
            <span className="text-sm font-medium">{confidence}%</span>
        </span>
    );
}

export default ConfidenceBreakdown;
