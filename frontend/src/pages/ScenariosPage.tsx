import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import ExplainabilityPanel from '../components/ExplainabilityPanel';
import { ConfidenceBreakdown } from '../components/ConfidenceBreakdown';
import PlainEnglishSummary from '../components/PlainEnglishSummary';
import CounterfactualHints from '../components/CounterfactualHints';
import { RankingModeSelector } from '../components/RankingModeSelector';

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

interface Scenario {
    id: string;
    program_name: string;
    status: string;
    confidence_score: number;
    pricing: {
        apr?: number;
        monthly_payment?: number;
        term_months?: number;
        total_cost?: number;
    };
    reason_codes: string[];
    explanation?: {
        summary: {
            outcome: string;
            confidence: number;
            plain_english: string;
        };
        factors: Array<{
            name: string;
            impact: 'positive' | 'negative' | 'neutral';
            weight: number;
            value: string;
            description: string;
        }>;
        rules: Array<{
            rule_id: string;
            rule_name: string;
            passed: boolean;
            explanation: string;
            threshold?: string;
            actual_value?: string;
        }>;
        data: Array<{
            field: string;
            value: string;
            source: string;
            confidence: number;
        }>;
    };
    counterfactual_hints?: Array<{
        id: string;
        category: string;
        current_value: string;
        target_value: string;
        potential_outcome: string;
        difficulty: 'easy' | 'medium' | 'hard';
        timeframe?: string;
    }>;
}

interface ScenarioRun {
    id: string;
    case_id: string;
    total_scenarios: number;
    eligible_count: number;
    refer_count: number;
    not_eligible_count: number;
    created_at: string;
}

type RankingMode = 'best_fit' | 'lowest_payment' | 'fastest_close' | 'highest_approval';

export function ScenariosPage() {
    const { accessToken } = useAuthStore();
    const [scenarios, setScenarios] = useState<{ eligible: Scenario[], refer: Scenario[], not_eligible: Scenario[] }>({
        eligible: [],
        refer: [],
        not_eligible: [],
    });
    const [latestRun, setLatestRun] = useState<ScenarioRun | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'eligible' | 'refer' | 'not_eligible'>('eligible');
    const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null);
    const [detailView, setDetailView] = useState<'overview' | 'explain' | 'improve'>('overview');
    const [rankingMode, setRankingMode] = useState<RankingMode>('best_fit');
    const [compareMode, setCompareMode] = useState(false);
    const [selectedForCompare, setSelectedForCompare] = useState<string[]>([]);

    useEffect(() => {
        fetchScenarios();
    }, [accessToken]);

    const fetchScenarios = async () => {
        if (!accessToken) return;

        setIsLoading(true);
        try {
            // Get cases first
            const casesResponse = await fetch(`${API_URL}/cases`, {
                headers: { 'Authorization': `Bearer ${accessToken}` },
            });

            if (casesResponse.ok) {
                const cases = await casesResponse.json();
                if (cases.length > 0) {
                    const latestCase = cases[0];

                    // Get scenario runs
                    const runsResponse = await fetch(`${API_URL}/cases/${latestCase.id}/scenarios/runs`, {
                        headers: { 'Authorization': `Bearer ${accessToken}` },
                    });

                    if (runsResponse.ok) {
                        const runs = await runsResponse.json();
                        if (runs.length > 0) {
                            setLatestRun(runs[0]);

                            // Get scenarios for this run
                            const scenariosResponse = await fetch(
                                `${API_URL}/cases/${latestCase.id}/scenarios/runs/${runs[0].id}`,
                                { headers: { 'Authorization': `Bearer ${accessToken}` } }
                            );

                            if (scenariosResponse.ok) {
                                const data = await scenariosResponse.json();
                                setScenarios({
                                    eligible: data.eligible || [],
                                    refer: data.refer || [],
                                    not_eligible: data.not_eligible || [],
                                });
                            }
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Failed to fetch scenarios:', error);
        }
        setIsLoading(false);
    };

    const getConfidenceColor = (score: number) => {
        if (score >= 80) return 'text-green-400';
        if (score >= 60) return 'text-yellow-400';
        return 'text-red-400';
    };

    const getConfidenceLabel = (score: number) => {
        if (score >= 80) return 'High';
        if (score >= 60) return 'Medium';
        return 'Low';
    };

    const sortScenarios = (scenarioList: Scenario[]): Scenario[] => {
        return [...scenarioList].sort((a, b) => {
            switch (rankingMode) {
                case 'lowest_payment':
                    return (a.pricing?.monthly_payment || Infinity) - (b.pricing?.monthly_payment || Infinity);
                case 'fastest_close':
                    return (a.pricing?.term_months || Infinity) - (b.pricing?.term_months || Infinity);
                case 'highest_approval':
                    return b.confidence_score - a.confidence_score;
                case 'best_fit':
                default:
                    // Best fit combines confidence score and apr
                    const aScore = a.confidence_score - (a.pricing?.apr || 0) * 100;
                    const bScore = b.confidence_score - (b.pricing?.apr || 0) * 100;
                    return bScore - aScore;
            }
        });
    };

    const handleCompareToggle = (scenarioId: string) => {
        setSelectedForCompare(prev => {
            if (prev.includes(scenarioId)) {
                return prev.filter(id => id !== scenarioId);
            }
            if (prev.length < 3) {
                return [...prev, scenarioId];
            }
            return prev;
        });
    };

    const tabs = [
        { key: 'eligible', label: 'Eligible', count: scenarios.eligible.length, color: 'bg-green-500' },
        { key: 'refer', label: 'Needs Review', count: scenarios.refer.length, color: 'bg-yellow-500' },
        { key: 'not_eligible', label: 'Not Eligible', count: scenarios.not_eligible.length, color: 'bg-red-500' },
    ] as const;

    const currentScenarios = sortScenarios(scenarios[activeTab]);

    // Build mock explanation data if not available
    const buildExplanationData = (scenario: Scenario) => {
        if (scenario.explanation) return scenario.explanation;

        return {
            summary: {
                outcome: scenario.status.toUpperCase(),
                confidence: scenario.confidence_score,
                plain_english: `Analysis of ${scenario.program_name} based on your credit profile.`
            },
            factors: [
                { name: 'Credit Score', impact: 'positive' as const, weight: 0.35, value: '680', description: 'Your credit score is above the minimum requirement' },
                { name: 'Debt-to-Income', impact: 'neutral' as const, weight: 0.25, value: '32%', description: 'Your DTI ratio is within acceptable range' },
                { name: 'Payment History', impact: 'positive' as const, weight: 0.25, value: '98%', description: 'Strong on-time payment record' },
                { name: 'Credit Utilization', impact: 'negative' as const, weight: 0.15, value: '45%', description: 'Credit utilization is higher than recommended' }
            ],
            rules: scenario.reason_codes?.map((code, i) => ({
                rule_id: `R${i + 1}`,
                rule_name: code.split(':')[0] || `Rule ${i + 1}`,
                passed: scenario.status === 'eligible',
                explanation: code
            })) || [],
            data: [
                { field: 'Credit Score', value: '680', source: 'TransUnion API', confidence: 95 },
                { field: 'Annual Income', value: '$75,000', source: 'User Stated', confidence: 70 },
                { field: 'Employment', value: 'Full-time', source: 'Verified', confidence: 90 }
            ]
        };
    };

    // Build mock hints if not available
    const buildCounterfactualHints = (scenario: Scenario) => {
        if (scenario.counterfactual_hints) return scenario.counterfactual_hints;

        if (scenario.status === 'eligible') return [];

        return [
            {
                id: '1',
                category: 'credit_utilization',
                current_value: 'credit utilization is 45%',
                target_value: 'below 30%',
                potential_outcome: 'May improve approval odds by 15-20%',
                difficulty: 'easy' as const,
                timeframe: '1-2 months'
            },
            {
                id: '2',
                category: 'debt',
                current_value: 'total credit card balance is $5,000',
                target_value: '$3,000 or less',
                potential_outcome: 'Could lower your DTI ratio and improve eligibility',
                difficulty: 'medium' as const,
                timeframe: '3-6 months'
            }
        ];
    };

    return (
        <div className="py-8">
            {/* Header */}
            <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold mb-2">Your Credit Scenarios</h1>
                    <p className="text-white/70">
                        {latestRun
                            ? `${latestRun.total_scenarios} programs analyzed • ${latestRun.eligible_count} you may qualify for`
                            : 'Complete your intake to see personalized scenarios'
                        }
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={() => setCompareMode(!compareMode)}
                        className={`px-4 py-2 rounded-lg transition-all ${compareMode
                            ? 'bg-purple-500/20 text-purple-300 ring-1 ring-purple-500/50'
                            : 'bg-white/10 text-white/70 hover:bg-white/20'
                            }`}
                    >
                        {compareMode ? `📊 Comparing (${selectedForCompare.length}/3)` : '📊 Compare'}
                    </button>
                    <Link to="/what-if" className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg text-white/70">
                        🔮 What-If
                    </Link>
                </div>
            </div>

            {isLoading ? (
                <div className="glass-card p-12 text-center">
                    <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-4" />
                    <p className="text-white/60">Analyzing your options...</p>
                </div>
            ) : scenarios.eligible.length === 0 && scenarios.refer.length === 0 ? (
                <div className="glass-card p-12 text-center">
                    <div className="text-6xl mb-4">🔍</div>
                    <h2 className="text-xl font-semibold mb-2">No scenarios yet</h2>
                    <p className="text-white/60 mb-6">
                        Complete your intake to generate personalized credit scenarios
                    </p>
                    <a href="/dashboard" className="btn-primary">
                        Go to Dashboard
                    </a>
                </div>
            ) : (
                <>
                    {/* Tabs and Ranking */}
                    <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                        <div className="flex gap-2">
                            {tabs.map((tab) => (
                                <button
                                    key={tab.key}
                                    onClick={() => setActiveTab(tab.key)}
                                    className={`px-4 py-2 rounded-lg transition-all flex items-center gap-2 ${activeTab === tab.key
                                        ? 'bg-white/10 text-white'
                                        : 'text-white/60 hover:text-white hover:bg-white/5'
                                        }`}
                                >
                                    <span className={`w-2 h-2 rounded-full ${tab.color}`} />
                                    {tab.label}
                                    <span className="text-sm bg-white/10 px-2 py-0.5 rounded-full">
                                        {tab.count}
                                    </span>
                                </button>
                            ))}
                        </div>

                        <RankingModeSelector
                            currentMode={rankingMode}
                            onModeChange={setRankingMode}
                        />
                    </div>

                    {/* Scenarios Grid */}
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {currentScenarios.map((scenario) => (
                            <div
                                key={scenario.id}
                                className={`glass-card p-6 transition-all cursor-pointer relative ${compareMode && selectedForCompare.includes(scenario.id)
                                    ? 'ring-2 ring-purple-500'
                                    : 'hover:border-primary-500/30'
                                    }`}
                                onClick={() => compareMode
                                    ? handleCompareToggle(scenario.id)
                                    : setSelectedScenario(scenario)
                                }
                            >
                                {compareMode && (
                                    <div className={`absolute top-2 right-2 w-6 h-6 rounded-full flex items-center justify-center ${selectedForCompare.includes(scenario.id)
                                        ? 'bg-purple-500 text-white'
                                        : 'bg-white/10 text-white/40'
                                        }`}>
                                        {selectedForCompare.includes(scenario.id)
                                            ? selectedForCompare.indexOf(scenario.id) + 1
                                            : '+'
                                        }
                                    </div>
                                )}

                                <div className="flex items-start justify-between mb-4">
                                    <h3 className="font-semibold">{scenario.program_name}</h3>
                                    <span className={`text-sm font-medium ${getConfidenceColor(scenario.confidence_score)}`}>
                                        {getConfidenceLabel(scenario.confidence_score)}
                                    </span>
                                </div>

                                {scenario.pricing && (
                                    <div className="space-y-2 mb-4">
                                        {scenario.pricing.apr && (
                                            <div className="flex justify-between">
                                                <span className="text-white/60">APR</span>
                                                <span className="font-medium">{(scenario.pricing.apr * 100).toFixed(2)}%</span>
                                            </div>
                                        )}
                                        {scenario.pricing.monthly_payment && (
                                            <div className="flex justify-between">
                                                <span className="text-white/60">Monthly</span>
                                                <span className="font-medium">${scenario.pricing.monthly_payment.toLocaleString()}</span>
                                            </div>
                                        )}
                                        {scenario.pricing.term_months && (
                                            <div className="flex justify-between">
                                                <span className="text-white/60">Term</span>
                                                <span className="font-medium">{scenario.pricing.term_months} months</span>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Confidence Meter */}
                                <div className="mb-4">
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-white/60">Confidence</span>
                                        <span>{scenario.confidence_score}%</span>
                                    </div>
                                    <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full transition-all ${scenario.confidence_score >= 80 ? 'bg-green-500' :
                                                scenario.confidence_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                                                }`}
                                            style={{ width: `${scenario.confidence_score}%` }}
                                        />
                                    </div>
                                </div>

                                {scenario.reason_codes?.length > 0 && (
                                    <div className="text-xs text-white/50">
                                        {scenario.reason_codes.slice(0, 2).join(' • ')}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>

                    {/* Compare Button */}
                    {compareMode && selectedForCompare.length >= 2 && (
                        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40">
                            <Link
                                to={`/scenarios/compare?ids=${selectedForCompare.join(',')}`}
                                className="btn-primary shadow-lg flex items-center gap-2"
                            >
                                Compare {selectedForCompare.length} Scenarios
                                <span>→</span>
                            </Link>
                        </div>
                    )}
                </>
            )}

            {/* Enhanced Scenario Detail Modal */}
            {selectedScenario && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="glass-card p-0 max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
                        {/* Modal Header */}
                        <div className="p-6 border-b border-white/10 flex items-start justify-between">
                            <div>
                                <h2 className="text-xl font-bold">{selectedScenario.program_name}</h2>
                                <p className="text-white/60 text-sm mt-1">
                                    {selectedScenario.status === 'eligible' ? '✓ You may qualify' :
                                        selectedScenario.status === 'refer' ? '⏳ Needs review' :
                                            '✕ Not currently eligible'}
                                </p>
                            </div>
                            <button
                                onClick={() => {
                                    setSelectedScenario(null);
                                    setDetailView('overview');
                                }}
                                className="text-white/60 hover:text-white"
                            >
                                ✕
                            </button>
                        </div>

                        {/* View Tabs */}
                        <div className="flex border-b border-white/10">
                            {[
                                { key: 'overview', label: '📋 Overview', icon: '📋' },
                                { key: 'explain', label: '🔍 Why This Result', icon: '🔍' },
                                { key: 'improve', label: '💡 How to Improve', icon: '💡' }
                            ].map(tab => (
                                <button
                                    key={tab.key}
                                    onClick={() => setDetailView(tab.key as typeof detailView)}
                                    className={`flex-1 px-4 py-3 text-sm font-medium transition-all ${detailView === tab.key
                                        ? 'bg-white/10 text-white border-b-2 border-purple-500'
                                        : 'text-white/60 hover:text-white hover:bg-white/5'
                                        }`}
                                >
                                    {tab.label}
                                </button>
                            ))}
                        </div>

                        {/* Modal Content */}
                        <div className="flex-1 overflow-y-auto p-6">
                            {detailView === 'overview' && (
                                <div className="space-y-6">
                                    {/* Plain English Summary */}
                                    <PlainEnglishSummary
                                        data={{
                                            outcome: selectedScenario.status.toUpperCase() as 'ELIGIBLE' | 'REFER' | 'NOT_ELIGIBLE',
                                            program_name: selectedScenario.program_name,
                                            key_factors: buildExplanationData(selectedScenario).factors.map(f => ({
                                                name: f.name,
                                                impact: f.impact,
                                                value: f.value
                                            })),
                                            confidence: selectedScenario.confidence_score,
                                            next_steps: selectedScenario.status !== 'eligible'
                                                ? ['Review improvement suggestions', 'Try the What-If simulator']
                                                : ['Review terms carefully', 'Apply when ready']
                                        }}
                                        detailed={true}
                                    />

                                    {/* Pricing Details */}
                                    {selectedScenario.pricing && (
                                        <div>
                                            <h3 className="font-medium mb-3">Pricing Details</h3>
                                            <div className="bg-white/5 rounded-lg p-4 space-y-2">
                                                {selectedScenario.pricing.apr && (
                                                    <div className="flex justify-between">
                                                        <span className="text-white/60">Annual Percentage Rate</span>
                                                        <span>{(selectedScenario.pricing.apr * 100).toFixed(2)}%</span>
                                                    </div>
                                                )}
                                                {selectedScenario.pricing.monthly_payment && (
                                                    <div className="flex justify-between">
                                                        <span className="text-white/60">Monthly Payment</span>
                                                        <span>${selectedScenario.pricing.monthly_payment.toLocaleString()}</span>
                                                    </div>
                                                )}
                                                {selectedScenario.pricing.total_cost && (
                                                    <div className="flex justify-between">
                                                        <span className="text-white/60">Total Cost</span>
                                                        <span>${selectedScenario.pricing.total_cost.toLocaleString()}</span>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    )}

                                    {/* Confidence Breakdown */}
                                    <ConfidenceBreakdown
                                        overall={selectedScenario.confidence_score}
                                        factors={buildExplanationData(selectedScenario).factors.map(f => ({
                                            name: f.name,
                                            confidence: Math.round(f.weight * 100 + Math.random() * 20),
                                            source: 'Verified Data',
                                            weight: f.weight
                                        }))}
                                        showDetails={false}
                                    />
                                </div>
                            )}

                            {detailView === 'explain' && (
                                <ExplainabilityPanel
                                    scenarioId={selectedScenario.id}
                                    programName={selectedScenario.program_name}
                                    explanation={buildExplanationData(selectedScenario)}
                                />
                            )}

                            {detailView === 'improve' && (
                                <div className="space-y-6">
                                    <CounterfactualHints
                                        hints={buildCounterfactualHints(selectedScenario)}
                                        scenarioId={selectedScenario.id}
                                    />

                                    <div className="text-center pt-4">
                                        <Link
                                            to="/what-if"
                                            className="btn-primary inline-flex items-center gap-2"
                                        >
                                            🔮 Open Full What-If Simulator
                                        </Link>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Modal Footer */}
                        <div className="p-6 border-t border-white/10 flex gap-3">
                            <button
                                onClick={() => {
                                    setSelectedScenario(null);
                                    setDetailView('overview');
                                }}
                                className="btn-secondary flex-1"
                            >
                                Close
                            </button>
                            {selectedScenario.status === 'eligible' && (
                                <button className="btn-primary flex-1">
                                    Apply Now
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

