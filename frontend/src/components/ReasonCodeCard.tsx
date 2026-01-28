

interface ReasonCode {
    code: string;
    category: string;
    description: string;
    severity: 'high' | 'medium' | 'low';
    improvement_action?: string;
}

interface ReasonCodeCardProps {
    code: ReasonCode;
    showAction?: boolean;
}

/**
 * ReasonCodeCard Component
 * 
 * Displays a reason code with visual styling based on severity.
 * Includes improvement action if available.
 * Uses adverse-action-safe language.
 */
export function ReasonCodeCard({ code, showAction = true }: ReasonCodeCardProps) {
    const getSeverityStyles = (severity: string): { bg: string; border: string; badge: string } => {
        switch (severity) {
            case 'high':
                return {
                    bg: 'bg-red-500/10',
                    border: 'border-red-500/30',
                    badge: 'bg-red-500/20 text-red-300'
                };
            case 'medium':
                return {
                    bg: 'bg-yellow-500/10',
                    border: 'border-yellow-500/30',
                    badge: 'bg-yellow-500/20 text-yellow-300'
                };
            case 'low':
                return {
                    bg: 'bg-blue-500/10',
                    border: 'border-blue-500/30',
                    badge: 'bg-blue-500/20 text-blue-300'
                };
            default:
                return {
                    bg: 'bg-white/5',
                    border: 'border-white/20',
                    badge: 'bg-white/20 text-white/70'
                };
        }
    };

    const getCategoryIcon = (category: string): string => {
        const icons: Record<string, string> = {
            'credit_history': '📊',
            'income': '💰',
            'employment': '💼',
            'debt': '💳',
            'collateral': '🏠',
            'documentation': '📄',
            'identity': '🆔',
            'other': '📋'
        };
        return icons[category] || '📋';
    };

    const styles = getSeverityStyles(code.severity);

    return (
        <div className={`rounded-lg p-4 border ${styles.bg} ${styles.border}`}>
            <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                    <span className="text-xl">{getCategoryIcon(code.category)}</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${styles.badge}`}>
                        {code.code}
                    </span>
                </div>
                <span className={`text-xs capitalize ${styles.badge.replace('text-', 'text-')}`}>
                    {code.severity} Impact
                </span>
            </div>

            <p className="text-white/80 text-sm mb-2">{code.description}</p>

            {showAction && code.improvement_action && (
                <div className="mt-3 pt-3 border-t border-white/10">
                    <p className="text-purple-300 text-sm flex items-start gap-2">
                        <span>💡</span>
                        <span>{code.improvement_action}</span>
                    </p>
                </div>
            )}
        </div>
    );
}

interface ReasonCodeListProps {
    codes: ReasonCode[];
    groupBySeverity?: boolean;
}

/**
 * ReasonCodeList Component
 * 
 * Displays a list of reason codes, optionally grouped by severity.
 */
export function ReasonCodeList({ codes, groupBySeverity = false }: ReasonCodeListProps) {
    if (!groupBySeverity) {
        return (
            <div className="space-y-3">
                {codes.map(code => (
                    <ReasonCodeCard key={code.code} code={code} />
                ))}
            </div>
        );
    }

    // Group by severity
    const grouped = {
        high: codes.filter(c => c.severity === 'high'),
        medium: codes.filter(c => c.severity === 'medium'),
        low: codes.filter(c => c.severity === 'low')
    };

    return (
        <div className="space-y-6">
            {grouped.high.length > 0 && (
                <div>
                    <h4 className="text-red-300 text-sm font-medium mb-3">High Impact</h4>
                    <div className="space-y-2">
                        {grouped.high.map(code => (
                            <ReasonCodeCard key={code.code} code={code} />
                        ))}
                    </div>
                </div>
            )}
            {grouped.medium.length > 0 && (
                <div>
                    <h4 className="text-yellow-300 text-sm font-medium mb-3">Medium Impact</h4>
                    <div className="space-y-2">
                        {grouped.medium.map(code => (
                            <ReasonCodeCard key={code.code} code={code} />
                        ))}
                    </div>
                </div>
            )}
            {grouped.low.length > 0 && (
                <div>
                    <h4 className="text-blue-300 text-sm font-medium mb-3">Low Impact</h4>
                    <div className="space-y-2">
                        {grouped.low.map(code => (
                            <ReasonCodeCard key={code.code} code={code} />
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

// Sample reason codes mapping for reference
export const REASON_CODE_DEFINITIONS: Record<string, Omit<ReasonCode, 'code'>> = {
    'RC001': {
        category: 'credit_history',
        description: 'Limited credit history length',
        severity: 'medium',
        improvement_action: 'Continue using existing credit accounts responsibly to build history'
    },
    'RC002': {
        category: 'income',
        description: 'Income verification pending',
        severity: 'low',
        improvement_action: 'Provide recent pay stubs or bank statements to verify income'
    },
    'RC003': {
        category: 'debt',
        description: 'High debt-to-income ratio',
        severity: 'high',
        improvement_action: 'Consider paying down existing debts before applying'
    },
    'RC004': {
        category: 'employment',
        description: 'Employment length below threshold',
        severity: 'medium',
        improvement_action: 'Provide additional employment history documentation'
    },
    'RC005': {
        category: 'credit_history',
        description: 'Recent hard inquiries detected',
        severity: 'low',
        improvement_action: 'Wait 6+ months before applying to reduce inquiry impact'
    }
};

export default ReasonCodeCard;
