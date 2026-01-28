import { useState } from 'react';
import { Link } from 'react-router-dom';

interface CounterfactualHint {
    id: string;
    category: string;
    current_value: string;
    target_value: string;
    potential_outcome: string;
    difficulty: 'easy' | 'medium' | 'hard';
    timeframe?: string;
    simulation_link?: string;
}

interface CounterfactualHintsProps {
    hints: CounterfactualHint[];
    scenarioId?: string;
    onSimulate?: (hintId: string) => void;
}

/**
 * CounterfactualHints Component
 * 
 * Shows "If X changes to Y, then Z might happen" suggestions.
 * Uses conditional language to avoid guarantees.
 */
export function CounterfactualHints({
    hints,
    scenarioId: _scenarioId,
    onSimulate
}: CounterfactualHintsProps) {
    const [expanded, setExpanded] = useState<string | null>(null);

    const getDifficultyStyles = (difficulty: string) => {
        switch (difficulty) {
            case 'easy': return { bg: 'bg-green-500/20', text: 'text-green-300', label: 'Quick Win' };
            case 'medium': return { bg: 'bg-yellow-500/20', text: 'text-yellow-300', label: 'Moderate Effort' };
            case 'hard': return { bg: 'bg-red-500/20', text: 'text-red-300', label: 'Significant Change' };
            default: return { bg: 'bg-white/20', text: 'text-white/60', label: 'Unknown' };
        }
    };

    const getCategoryIcon = (category: string) => {
        const icons: Record<string, string> = {
            'credit_utilization': '💳',
            'income': '💰',
            'debt': '📊',
            'employment': '💼',
            'savings': '🏦',
            'documentation': '📄',
            'time': '⏰',
            'other': '💡'
        };
        return icons[category] || '💡';
    };

    if (hints.length === 0) {
        return (
            <div className="glass rounded-xl p-6 text-center">
                <div className="text-4xl mb-3">✨</div>
                <p className="text-white/60">No improvement suggestions available</p>
                <p className="text-white/40 text-sm mt-1">
                    Your profile already meets the criteria for this scenario
                </p>
            </div>
        );
    }

    return (
        <div className="glass rounded-xl overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-white/10 bg-white/5">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                    <span>🔮</span>
                    What If...?
                </h2>
                <p className="text-white/50 text-sm mt-1">
                    Explore how changes might affect your eligibility
                </p>
            </div>

            {/* Hints List */}
            <div className="p-4 space-y-3">
                {hints.map(hint => {
                    const diffStyles = getDifficultyStyles(hint.difficulty);
                    const isExpanded = expanded === hint.id;

                    return (
                        <div
                            key={hint.id}
                            className={`bg-white/5 rounded-lg border border-white/10 overflow-hidden transition-all ${isExpanded ? 'ring-1 ring-purple-500/50' : ''
                                }`}
                        >
                            <button
                                onClick={() => setExpanded(isExpanded ? null : hint.id)}
                                className="w-full p-4 text-left flex items-start gap-3"
                            >
                                <span className="text-2xl">{getCategoryIcon(hint.category)}</span>
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className={`text-xs px-2 py-0.5 rounded-full ${diffStyles.bg} ${diffStyles.text}`}>
                                            {diffStyles.label}
                                        </span>
                                        {hint.timeframe && (
                                            <span className="text-white/40 text-xs">
                                                ~{hint.timeframe}
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-white/80">
                                        <span className="text-white/50">If </span>
                                        <span className="text-white">{hint.current_value}</span>
                                        <span className="text-white/50"> changes to </span>
                                        <span className="text-purple-300">{hint.target_value}</span>
                                    </p>
                                </div>
                                <span className={`text-white/40 transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
                                    ▼
                                </span>
                            </button>

                            {/* Expanded Content */}
                            {isExpanded && (
                                <div className="px-4 pb-4 pt-2 border-t border-white/5">
                                    <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-3 mb-3">
                                        <p className="text-purple-200 text-sm">
                                            <span className="text-purple-400">Potential outcome: </span>
                                            {hint.potential_outcome}
                                        </p>
                                    </div>

                                    <div className="flex gap-2">
                                        {onSimulate && (
                                            <button
                                                onClick={() => onSimulate(hint.id)}
                                                className="bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 px-4 py-2 rounded-lg text-sm transition-colors"
                                            >
                                                🧪 Simulate This
                                            </button>
                                        )}
                                        {hint.simulation_link && (
                                            <Link
                                                to={hint.simulation_link}
                                                className="bg-white/10 hover:bg-white/20 text-white/80 px-4 py-2 rounded-lg text-sm transition-colors"
                                            >
                                                Open What-If Tool →
                                            </Link>
                                        )}
                                    </div>

                                    <p className="text-white/30 text-xs mt-3">
                                        ⚠️ This is a simulation only. Actual results may vary.
                                    </p>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Footer */}
            <div className="p-4 bg-white/5 border-t border-white/10">
                <div className="flex items-center justify-between">
                    <p className="text-white/40 text-sm">
                        {hints.length} suggestion{hints.length !== 1 ? 's' : ''} available
                    </p>
                    <Link
                        to="/what-if"
                        className="text-purple-400 hover:text-purple-300 text-sm flex items-center gap-1"
                    >
                        Open Full Simulator →
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default CounterfactualHints;
