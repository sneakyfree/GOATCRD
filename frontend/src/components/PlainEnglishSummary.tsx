/**
 * PlainEnglishSummary Component
 * 
 * Generates and displays natural language explanations
 * of credit decisions using template-based approach.
 */

interface SummaryData {
    outcome: 'ELIGIBLE' | 'REFER' | 'NOT_ELIGIBLE';
    program_name: string;
    key_factors: Array<{
        name: string;
        impact: 'positive' | 'negative' | 'neutral';
        value?: string;
    }>;
    top_reason_code?: string;
    confidence: number;
    next_steps?: string[];
}

interface PlainEnglishSummaryProps {
    data: SummaryData;
    detailed?: boolean;
}

export function PlainEnglishSummary({ data, detailed = false }: PlainEnglishSummaryProps) {
    const generateSummary = (): string => {
        const { outcome, program_name, key_factors, confidence } = data;

        const positiveFactors = key_factors.filter(f => f.impact === 'positive');
        const negativeFactors = key_factors.filter(f => f.impact === 'negative');

        let summary = '';

        switch (outcome) {
            case 'ELIGIBLE':
                summary = `Based on our analysis, you appear to meet the requirements for ${program_name}. `;
                if (positiveFactors.length > 0) {
                    summary += `Key strengths include your ${positiveFactors.map(f => f.name.toLowerCase()).join(', ')}. `;
                }
                if (confidence >= 80) {
                    summary += `We have high confidence (${confidence}%) in this assessment.`;
                } else {
                    summary += `Confidence level is ${confidence}%, and some factors may need verification.`;
                }
                break;

            case 'REFER':
                summary = `Your application for ${program_name} requires additional review. `;
                if (negativeFactors.length > 0) {
                    summary += `The main areas of concern are your ${negativeFactors.map(f => f.name.toLowerCase()).join(' and ')}. `;
                }
                summary += `A human reviewer will evaluate your case for final determination. `;
                if (positiveFactors.length > 0) {
                    summary += `However, your ${positiveFactors[0].name.toLowerCase()} works in your favor.`;
                }
                break;

            case 'NOT_ELIGIBLE':
                summary = `Unfortunately, you do not currently meet the requirements for ${program_name}. `;
                if (negativeFactors.length > 0) {
                    summary += `The primary reasons relate to your ${negativeFactors.map(f => f.name.toLowerCase()).join(' and ')}. `;
                }
                summary += `Please see the improvement suggestions below for ways you might become eligible in the future.`;
                break;
        }

        return summary;
    };

    const getOutcomeStyles = (outcome: string) => {
        switch (outcome) {
            case 'ELIGIBLE': return { bg: 'bg-green-500/10', border: 'border-green-500/30', icon: '✓', text: 'text-green-300' };
            case 'REFER': return { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', icon: '⏳', text: 'text-yellow-300' };
            case 'NOT_ELIGIBLE': return { bg: 'bg-red-500/10', border: 'border-red-500/30', icon: '✕', text: 'text-red-300' };
            default: return { bg: 'bg-white/10', border: 'border-white/30', icon: '?', text: 'text-white/60' };
        }
    };

    const styles = getOutcomeStyles(data.outcome);

    return (
        <div className={`rounded-xl p-6 ${styles.bg} border ${styles.border}`}>
            {/* Header */}
            <div className="flex items-center gap-3 mb-4">
                <span className={`w-10 h-10 rounded-full flex items-center justify-center text-xl ${styles.bg} ${styles.text}`}>
                    {styles.icon}
                </span>
                <div>
                    <h3 className="text-white font-semibold">Decision Summary</h3>
                    <p className={`text-sm ${styles.text}`}>
                        {data.outcome.replace('_', ' ')} for {data.program_name}
                    </p>
                </div>
            </div>

            {/* Plain English Summary */}
            <p className="text-white/80 leading-relaxed mb-4">
                {generateSummary()}
            </p>

            {/* Detailed View */}
            {detailed && (
                <>
                    {/* Key Factors */}
                    <div className="mb-4">
                        <h4 className="text-white/60 text-sm mb-2">Key Factors:</h4>
                        <div className="flex flex-wrap gap-2">
                            {data.key_factors.map((factor, i) => (
                                <span
                                    key={i}
                                    className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm ${factor.impact === 'positive' ? 'bg-green-500/20 text-green-300' :
                                            factor.impact === 'negative' ? 'bg-red-500/20 text-red-300' :
                                                'bg-white/10 text-white/60'
                                        }`}
                                >
                                    <span>{factor.impact === 'positive' ? '↑' : factor.impact === 'negative' ? '↓' : '→'}</span>
                                    {factor.name}
                                    {factor.value && <span className="opacity-70">({factor.value})</span>}
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* Next Steps */}
                    {data.next_steps && data.next_steps.length > 0 && (
                        <div className="pt-4 border-t border-white/10">
                            <h4 className="text-white/60 text-sm mb-2">Recommended Next Steps:</h4>
                            <ul className="space-y-2">
                                {data.next_steps.map((step, i) => (
                                    <li key={i} className="flex items-start gap-2 text-white/80 text-sm">
                                        <span className="text-purple-400">→</span>
                                        {step}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </>
            )}

            {/* Disclaimer */}
            <p className="text-white/30 text-xs mt-4">
                This is a preliminary assessment. Final determination may differ after full review.
            </p>
        </div>
    );
}

export default PlainEnglishSummary;
