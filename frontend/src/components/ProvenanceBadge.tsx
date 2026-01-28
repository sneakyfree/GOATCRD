
interface ProvenanceBadgeProps {
    source: string;
    confidence: number;
    timestamp?: string;
    fieldName?: string;
    onVerify?: () => void;
}

/**
 * ProvenanceBadge Component
 * 
 * Displays the source and confidence of a data field value.
 * Color-coded by verification status:
 * - Green (verified): 80%+ confidence, verified source
 * - Yellow (provided): 60%+ confidence, user-provided
 * - Orange (estimated): <60% confidence or estimated
 * - Red (unknown): No source information
 */
export function ProvenanceBadge({
    source,
    confidence,
    timestamp,
    fieldName: _fieldName,
    onVerify
}: ProvenanceBadgeProps) {
    const getSourceLabel = (source: string): string => {
        const labels: Record<string, string> = {
            'payroll_api': 'Payroll Verified',
            'credit_bureau': 'Bureau Verified',
            'bank_api': 'Bank Verified',
            'tax_return': 'Tax Return',
            'user_stated': 'User Provided',
            'estimated': 'Estimated',
            'derived': 'Calculated',
            'unknown': 'Unknown'
        };
        return labels[source] || source;
    };

    const getSourceColor = (source: string, confidence: number): string => {
        if (source === 'unknown') return 'bg-red-500/20 text-red-300 border-red-500/30';
        if (source === 'estimated' || confidence < 60) return 'bg-orange-500/20 text-orange-300 border-orange-500/30';
        if (source === 'user_stated' || (confidence >= 60 && confidence < 80)) return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
        return 'bg-green-500/20 text-green-300 border-green-500/30';
    };

    const getSourceIcon = (source: string): string => {
        const icons: Record<string, string> = {
            'payroll_api': '✓',
            'credit_bureau': '✓',
            'bank_api': '✓',
            'tax_return': '📄',
            'user_stated': '👤',
            'estimated': '~',
            'derived': '∑',
            'unknown': '?'
        };
        return icons[source] || '•';
    };

    const showVerifyButton = confidence < 80 && source !== 'unknown' && onVerify;

    return (
        <div className="inline-flex items-center gap-2">
            <span
                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs border ${getSourceColor(source, confidence)}`}
                title={`Source: ${getSourceLabel(source)} | Confidence: ${confidence}% ${timestamp ? `| Verified: ${new Date(timestamp).toLocaleDateString()}` : ''}`}
            >
                <span>{getSourceIcon(source)}</span>
                <span>{getSourceLabel(source)}</span>
                <span className="opacity-60">({confidence}%)</span>
            </span>
            {showVerifyButton && (
                <button
                    onClick={onVerify}
                    className="text-purple-400 hover:text-purple-300 text-xs underline"
                >
                    Verify
                </button>
            )}
        </div>
    );
}

/**
 * ProvenanceBadgeCompact
 * 
 * Compact version showing just the icon and tooltip
 */
export function ProvenanceBadgeCompact({
    source,
    confidence,
    timestamp: _timestamp
}: Omit<ProvenanceBadgeProps, 'onVerify' | 'fieldName'>) {
    const getSourceColor = (source: string, confidence: number): string => {
        if (source === 'unknown') return 'text-red-400';
        if (source === 'estimated' || confidence < 60) return 'text-orange-400';
        if (source === 'user_stated' || (confidence >= 60 && confidence < 80)) return 'text-yellow-400';
        return 'text-green-400';
    };

    const getSourceIcon = (source: string): string => {
        const icons: Record<string, string> = {
            'payroll_api': '✓',
            'credit_bureau': '✓',
            'bank_api': '✓',
            'user_stated': '👤',
            'estimated': '~',
            'unknown': '?'
        };
        return icons[source] || '•';
    };

    return (
        <span
            className={`cursor-help ${getSourceColor(source, confidence)}`}
            title={`Source: ${source} | Confidence: ${confidence}%`}
        >
            {getSourceIcon(source)}
        </span>
    );
}

export default ProvenanceBadge;
