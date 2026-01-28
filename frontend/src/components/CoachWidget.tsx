import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

/**
 * CoachWidget Component
 * 
 * Proactive improvement suggestions for the consumer.
 * Uses "If-then" language without guarantees.
 * Integrates with What-If simulator.
 */

interface CoachSuggestion {
    id: string;
    category: string;
    suggestion: string;
    potential_impact: string;
    confidence: number;
    action_link?: string;
    dismissed?: boolean;
}

export function CoachWidget() {
    const [suggestions, setSuggestions] = useState<CoachSuggestion[]>([]);
    const [loading, setLoading] = useState(true);
    const [collapsed, setCollapsed] = useState(false);

    useEffect(() => {
        // Fetch personalized suggestions
        const fetchSuggestions = async () => {
            // Mock suggestions for demo
            const mockSuggestions: CoachSuggestion[] = [
                {
                    id: 'sug-001',
                    category: 'credit_utilization',
                    suggestion: 'If you reduce credit utilization below 30%, you may see improved eligibility for premium programs.',
                    potential_impact: 'Could unlock 2 additional scenarios',
                    confidence: 75,
                    action_link: '/what-if?simulate=credit_utilization'
                },
                {
                    id: 'sug-002',
                    category: 'income_verification',
                    suggestion: 'Linking your bank account could increase income confidence from 60% to 95%.',
                    potential_impact: 'May improve pricing by up to 1.5%',
                    confidence: 85,
                    action_link: '/alternative-data'
                },
                {
                    id: 'sug-003',
                    category: 'documentation',
                    suggestion: 'Adding 2 recent pay stubs could help verify employment length.',
                    potential_impact: 'May change status from REFER to ELIGIBLE',
                    confidence: 70
                }
            ];

            setSuggestions(mockSuggestions);
            setLoading(false);
        };

        fetchSuggestions();
    }, []);

    const dismissSuggestion = (id: string) => {
        setSuggestions(prev =>
            prev.map(s => s.id === id ? { ...s, dismissed: true } : s)
        );
    };

    const saveSuggestion = (id: string) => {
        // Would save to backend for later
        console.log('Saved suggestion:', id);
    };

    const getCategoryIcon = (category: string): string => {
        const icons: Record<string, string> = {
            'credit_utilization': '💳',
            'income_verification': '💰',
            'documentation': '📄',
            'employment': '💼',
            'debt_reduction': '📉',
            'account_age': '⏰'
        };
        return icons[category] || '💡';
    };

    const activeSuggestions = suggestions.filter(s => !s.dismissed);

    if (loading) {
        return (
            <div className="glass rounded-xl p-4">
                <div className="animate-pulse flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-white/10"></div>
                    <div className="flex-1">
                        <div className="h-4 bg-white/10 rounded w-3/4"></div>
                        <div className="h-3 bg-white/10 rounded w-1/2 mt-2"></div>
                    </div>
                </div>
            </div>
        );
    }

    if (activeSuggestions.length === 0) {
        return null;
    }

    return (
        <div className="glass rounded-xl overflow-hidden">
            {/* Header */}
            <div
                className="flex items-center justify-between p-4 cursor-pointer hover:bg-white/5"
                onClick={() => setCollapsed(!collapsed)}
            >
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center text-xl">
                        🎯
                    </div>
                    <div>
                        <h3 className="text-white font-medium">Coach Suggestions</h3>
                        <p className="text-white/50 text-sm">{activeSuggestions.length} ways to potentially improve</p>
                    </div>
                </div>
                <button className="text-white/50 hover:text-white p-2">
                    {collapsed ? '▼' : '▲'}
                </button>
            </div>

            {/* Suggestions */}
            {!collapsed && (
                <div className="border-t border-white/10">
                    {activeSuggestions.map((suggestion, index) => (
                        <div
                            key={suggestion.id}
                            className={`p-4 ${index !== activeSuggestions.length - 1 ? 'border-b border-white/5' : ''}`}
                        >
                            <div className="flex items-start gap-3">
                                <span className="text-2xl">{getCategoryIcon(suggestion.category)}</span>
                                <div className="flex-1">
                                    <p className="text-white/80 text-sm">{suggestion.suggestion}</p>
                                    <p className="text-purple-300 text-xs mt-2">
                                        ✨ {suggestion.potential_impact}
                                    </p>

                                    {/* Actions */}
                                    <div className="flex items-center gap-2 mt-3">
                                        {suggestion.action_link && (
                                            <Link
                                                to={suggestion.action_link}
                                                className="bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 text-xs px-3 py-1 rounded-full transition-colors"
                                            >
                                                Try It →
                                            </Link>
                                        )}
                                        <button
                                            onClick={() => saveSuggestion(suggestion.id)}
                                            className="text-white/40 hover:text-white/60 text-xs"
                                        >
                                            Save for later
                                        </button>
                                        <button
                                            onClick={() => dismissSuggestion(suggestion.id)}
                                            className="text-white/40 hover:text-white/60 text-xs"
                                        >
                                            Dismiss
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}

                    {/* Disclaimer */}
                    <div className="p-3 bg-yellow-500/5 border-t border-yellow-500/20">
                        <p className="text-yellow-300/70 text-xs text-center">
                            ⚠️ Suggestions are for informational purposes only. Results are not guaranteed.
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}

export default CoachWidget;
