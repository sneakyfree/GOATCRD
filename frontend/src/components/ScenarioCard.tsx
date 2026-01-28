

interface ScenarioCardProps {
    scenario: {
        id: string;
        program_name: string;
        program_type: string;
        status: 'ELIGIBLE' | 'REFER' | 'NOT_ELIGIBLE';
        interest_rate?: number;
        monthly_payment?: number;
        max_loan_amount?: number;
        term_months?: number;
        confidence: number;
        reason_codes?: string[];
        provenance?: {
            data_sources: string[];
            rules_version: string;
        };
    };
    rank?: number;
    isRecommended?: boolean;
    onSelect?: () => void;
    onCompare?: () => void;
    showDetails?: boolean;
}

/**
 * ScenarioCard Component
 * 
 * Displays a single loan scenario with status, terms, and actions.
 * Includes provenance information and reason codes.
 */
export function ScenarioCard({
    scenario,
    rank,
    isRecommended = false,
    onSelect,
    onCompare,
    showDetails = false
}: ScenarioCardProps) {
    const getStatusStyles = (status: string) => {
        switch (status) {
            case 'ELIGIBLE':
                return {
                    bg: 'bg-green-500/20',
                    border: 'border-green-500/30',
                    text: 'text-green-300',
                    icon: '✓'
                };
            case 'REFER':
                return {
                    bg: 'bg-yellow-500/20',
                    border: 'border-yellow-500/30',
                    text: 'text-yellow-300',
                    icon: '⋯'
                };
            case 'NOT_ELIGIBLE':
                return {
                    bg: 'bg-red-500/20',
                    border: 'border-red-500/30',
                    text: 'text-red-300',
                    icon: '✕'
                };
            default:
                return {
                    bg: 'bg-white/10',
                    border: 'border-white/20',
                    text: 'text-white/60',
                    icon: '?'
                };
        }
    };

    const getProgramIcon = (type: string): string => {
        const icons: Record<string, string> = {
            'personal_loan': '💳',
            'mortgage': '🏠',
            'auto_loan': '🚗',
            'business_loan': '💼',
            'credit_card': '💳',
            'line_of_credit': '📊'
        };
        return icons[type] || '📄';
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    };

    const styles = getStatusStyles(scenario.status);

    return (
        <div className={`glass rounded-xl overflow-hidden ${isRecommended ? 'ring-2 ring-purple-500' : ''}`}>
            {/* Header */}
            <div className={`flex items-center justify-between p-4 ${styles.bg} border-b ${styles.border}`}>
                <div className="flex items-center gap-3">
                    {rank && (
                        <span className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-white font-bold text-sm">
                            #{rank}
                        </span>
                    )}
                    <span className="text-2xl">{getProgramIcon(scenario.program_type)}</span>
                    <div>
                        <h3 className="text-white font-semibold">{scenario.program_name}</h3>
                        <p className="text-white/50 text-sm capitalize">{scenario.program_type.replace('_', ' ')}</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {isRecommended && (
                        <span className="bg-purple-500/30 text-purple-300 text-xs px-2 py-1 rounded-full">
                            ⭐ Recommended
                        </span>
                    )}
                    <span className={`${styles.bg} ${styles.text} px-3 py-1 rounded-full text-sm flex items-center gap-1`}>
                        <span>{styles.icon}</span>
                        {scenario.status.replace('_', ' ')}
                    </span>
                </div>
            </div>

            {/* Body */}
            <div className="p-4">
                {scenario.status === 'ELIGIBLE' && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        {scenario.interest_rate !== undefined && (
                            <div>
                                <p className="text-white/50 text-sm">Rate</p>
                                <p className="text-white text-xl font-bold">{scenario.interest_rate.toFixed(2)}%</p>
                            </div>
                        )}
                        {scenario.monthly_payment !== undefined && (
                            <div>
                                <p className="text-white/50 text-sm">Monthly</p>
                                <p className="text-white text-xl font-bold">{formatCurrency(scenario.monthly_payment)}</p>
                            </div>
                        )}
                        {scenario.max_loan_amount !== undefined && (
                            <div>
                                <p className="text-white/50 text-sm">Max Amount</p>
                                <p className="text-white text-xl font-bold">{formatCurrency(scenario.max_loan_amount)}</p>
                            </div>
                        )}
                        {scenario.term_months !== undefined && (
                            <div>
                                <p className="text-white/50 text-sm">Term</p>
                                <p className="text-white text-xl font-bold">{scenario.term_months} mo</p>
                            </div>
                        )}
                    </div>
                )}

                {/* Confidence */}
                <div className="flex items-center gap-3 mb-4">
                    <p className="text-white/50 text-sm">Confidence:</p>
                    <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                        <div
                            className={`h-full rounded-full ${scenario.confidence >= 80 ? 'bg-green-500' :
                                scenario.confidence >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                                }`}
                            style={{ width: `${scenario.confidence}%` }}
                        />
                    </div>
                    <span className="text-white text-sm font-medium">{scenario.confidence}%</span>
                </div>

                {/* Reason Codes */}
                {scenario.reason_codes && scenario.reason_codes.length > 0 && (
                    <div className="mb-4">
                        <p className="text-white/50 text-sm mb-2">Considerations:</p>
                        <div className="flex flex-wrap gap-2">
                            {scenario.reason_codes.slice(0, 3).map((code, i) => (
                                <span key={i} className="bg-white/10 text-white/70 text-xs px-2 py-1 rounded">
                                    {code}
                                </span>
                            ))}
                            {scenario.reason_codes.length > 3 && (
                                <span className="text-white/40 text-xs">
                                    +{scenario.reason_codes.length - 3} more
                                </span>
                            )}
                        </div>
                    </div>
                )}

                {/* Provenance */}
                {showDetails && scenario.provenance && (
                    <div className="pt-4 border-t border-white/10">
                        <div className="flex items-center gap-4 text-xs text-white/40">
                            <span>Sources: {scenario.provenance.data_sources.join(', ')}</span>
                            <span>Rules: {scenario.provenance.rules_version}</span>
                        </div>
                    </div>
                )}

                {/* Actions */}
                <div className="flex gap-2 mt-4">
                    {onSelect && scenario.status === 'ELIGIBLE' && (
                        <button
                            onClick={onSelect}
                            className="flex-1 bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded-lg transition-colors"
                        >
                            Select This Option
                        </button>
                    )}
                    {onCompare && (
                        <button
                            onClick={onCompare}
                            className="bg-white/10 hover:bg-white/20 text-white py-2 px-4 rounded-lg transition-colors"
                        >
                            Compare
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}

export default ScenarioCard;
