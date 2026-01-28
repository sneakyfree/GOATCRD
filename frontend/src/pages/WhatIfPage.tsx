import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import PlainEnglishSummary from '../components/PlainEnglishSummary';
import { ConfidenceBreakdown } from '../components/ConfidenceBreakdown';

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

interface HypotheticalChange {
    field: string;
    label: string;
    currentValue: number;
    newValue: number;
    min: number;
    max: number;
    step: number;
    unit: string;
    category: string;
    isProtected?: boolean;
}

interface SimulationResult {
    status_changes: Array<{
        program_name: string;
        old_status: string;
        new_status: string;
        confidence_change?: number;
    }>;
    changes_summary: string[];
    confidence: string;
    confidence_reason: string;
    projected_outcomes?: {
        programs_unlocked: number;
        rate_improvement?: string;
        approval_lift?: string;
    };
}

const CHANGE_CATEGORIES = [
    { id: 'credit', label: '📊 Credit Profile', color: 'purple' },
    { id: 'income', label: '💰 Income & Debt', color: 'green' },
    { id: 'protected', label: '🛡️ Protected (Cannot Modify)', color: 'red' }
];

export function WhatIfPage() {
    const { accessToken } = useAuthStore();
    const [changes, setChanges] = useState<HypotheticalChange[]>([
        {
            field: 'credit_score',
            label: 'Credit Score',
            currentValue: 680,
            newValue: 680,
            min: 300,
            max: 850,
            step: 10,
            unit: 'points',
            category: 'credit',
        },
        {
            field: 'credit_utilization',
            label: 'Credit Utilization',
            currentValue: 45,
            newValue: 45,
            min: 0,
            max: 100,
            step: 5,
            unit: '%',
            category: 'credit',
        },
        {
            field: 'accounts_open',
            label: 'Open Accounts',
            currentValue: 5,
            newValue: 5,
            min: 0,
            max: 20,
            step: 1,
            unit: '',
            category: 'credit',
        },
        {
            field: 'debt_paydown',
            label: 'Pay Down Debt',
            currentValue: 0,
            newValue: 0,
            min: 0,
            max: 10000,
            step: 500,
            unit: '$',
            category: 'income',
        },
        {
            field: 'income_increase',
            label: 'Income Increase',
            currentValue: 0,
            newValue: 0,
            min: 0,
            max: 50000,
            step: 5000,
            unit: '$',
            category: 'income',
        },
        {
            field: 'months_employed',
            label: 'Months at Current Job',
            currentValue: 24,
            newValue: 24,
            min: 0,
            max: 120,
            step: 3,
            unit: 'months',
            category: 'income',
        },
        {
            field: 'race',
            label: 'Race/Ethnicity',
            currentValue: 0,
            newValue: 0,
            min: 0,
            max: 1,
            step: 1,
            unit: '',
            category: 'protected',
            isProtected: true,
        },
        {
            field: 'gender',
            label: 'Gender',
            currentValue: 0,
            newValue: 0,
            min: 0,
            max: 1,
            step: 1,
            unit: '',
            category: 'protected',
            isProtected: true,
        },
    ]);

    const [result, setResult] = useState<SimulationResult | null>(null);
    const [isSimulating, setIsSimulating] = useState(false);
    const [caseId, setCaseId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [activeCategory, setActiveCategory] = useState('credit');

    useEffect(() => {
        fetchLatestCase();
    }, [accessToken]);

    const fetchLatestCase = async () => {
        if (!accessToken) return;

        try {
            const response = await fetch(`${API_URL}/cases`, {
                headers: { 'Authorization': `Bearer ${accessToken}` },
            });

            if (response.ok) {
                const cases = await response.json();
                if (cases.length > 0) {
                    setCaseId(cases[0].id);
                }
            }
        } catch (err) {
            console.error('Failed to fetch cases:', err);
        }
    };

    const updateChange = (index: number, newValue: number) => {
        const change = changes[index];
        if (change.isProtected) return; // Block protected field changes

        setChanges(prev => prev.map((c, i) =>
            i === index ? { ...c, newValue } : c
        ));
    };

    const resetChanges = () => {
        setChanges(prev => prev.map(c => ({ ...c, newValue: c.currentValue })));
        setResult(null);
    };

    const runSimulation = async () => {
        if (!accessToken || !caseId) {
            setError('No active case found. Complete intake first.');
            return;
        }

        setIsSimulating(true);
        setError(null);

        try {
            // Build hypothetical changes object
            const hypotheticalChanges: Record<string, number> = {};
            changes.forEach(change => {
                if (change.newValue !== change.currentValue && !change.isProtected) {
                    hypotheticalChanges[change.field] = change.newValue;
                }
            });

            const response = await fetch(`${API_URL}/cases/${caseId}/scenarios/simulate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`,
                },
                body: JSON.stringify({ hypothetical_changes: hypotheticalChanges }),
            });

            if (response.ok) {
                const data = await response.json();
                setResult(data);
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Simulation failed');
            }
        } catch (err) {
            console.error('Simulation failed:', err);
            setError('Network error. Please try again.');
        }

        setIsSimulating(false);
    };

    const hasChanges = changes.some(c => c.newValue !== c.currentValue && !c.isProtected);
    const changedFields = changes.filter(c => c.newValue !== c.currentValue && !c.isProtected);
    const filteredChanges = changes.filter(c => c.category === activeCategory);

    // Build summary data for PlainEnglishSummary
    const buildSummaryData = () => {
        if (!result) return null;

        const hasPositiveChanges = result.status_changes.some(
            sc => (sc.new_status === 'eligible' && sc.old_status !== 'eligible') ||
                (sc.new_status === 'refer' && sc.old_status === 'not_eligible')
        );

        return {
            outcome: hasPositiveChanges ? 'ELIGIBLE' as const : 'REFER' as const,
            program_name: `${result.status_changes.length} programs analyzed`,
            key_factors: changedFields.map(cf => ({
                name: cf.label,
                impact: cf.newValue > cf.currentValue ? 'positive' as const : 'negative' as const,
                value: `${cf.currentValue} → ${cf.newValue}${cf.unit}`
            })),
            confidence: result.confidence === 'high' ? 85 : result.confidence === 'medium' ? 65 : 45,
            next_steps: result.changes_summary
        };
    };

    return (
        <div className="py-8">
            {/* Header */}
            <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold mb-2 flex items-center gap-2">
                        <span>🔮</span> What-If Simulator
                    </h1>
                    <p className="text-white/70">
                        Explore how changes to your financial profile could affect your options
                    </p>
                </div>
                <Link
                    to="/scenarios"
                    className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg text-white/70 flex items-center gap-2"
                >
                    ← Back to Scenarios
                </Link>
            </div>

            {/* Changes Preview Bar */}
            {hasChanges && (
                <div className="glass-card p-4 mb-6 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <span className="text-purple-400">
                            {changedFields.length} change{changedFields.length !== 1 ? 's' : ''} pending
                        </span>
                        <div className="flex gap-2">
                            {changedFields.slice(0, 3).map(cf => (
                                <span
                                    key={cf.field}
                                    className="text-xs bg-purple-500/20 text-purple-300 px-2 py-1 rounded"
                                >
                                    {cf.label}: {cf.currentValue} → {cf.newValue}
                                </span>
                            ))}
                            {changedFields.length > 3 && (
                                <span className="text-xs text-white/40">
                                    +{changedFields.length - 3} more
                                </span>
                            )}
                        </div>
                    </div>
                    <button
                        onClick={resetChanges}
                        className="text-white/50 hover:text-white text-sm"
                    >
                        Reset All
                    </button>
                </div>
            )}

            <div className="grid lg:grid-cols-2 gap-8">
                {/* Controls */}
                <div className="glass-card p-6">
                    <h2 className="text-lg font-semibold mb-4">Adjust Your Profile</h2>

                    {/* Category Tabs */}
                    <div className="flex gap-2 mb-6 border-b border-white/10 pb-3">
                        {CHANGE_CATEGORIES.map(cat => (
                            <button
                                key={cat.id}
                                onClick={() => setActiveCategory(cat.id)}
                                className={`px-4 py-2 rounded-lg text-sm transition-all ${activeCategory === cat.id
                                    ? `bg-${cat.color}-500/20 text-${cat.color}-300 ring-1 ring-${cat.color}-500/50`
                                    : 'text-white/60 hover:text-white hover:bg-white/5'
                                    }`}
                            >
                                {cat.label}
                            </button>
                        ))}
                    </div>

                    <div className="space-y-6">
                        {filteredChanges.map((change) => {
                            const globalIndex = changes.findIndex(c => c.field === change.field);
                            const hasChanged = change.newValue !== change.currentValue;

                            return (
                                <div
                                    key={change.field}
                                    className={`${change.isProtected ? 'opacity-50' : ''} ${hasChanged ? 'bg-purple-500/5 -mx-4 px-4 py-3 rounded-lg border border-purple-500/20' : ''
                                        }`}
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <label className="text-sm font-medium text-white/80 flex items-center gap-2">
                                            {change.label}
                                            {change.isProtected && (
                                                <span className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded">
                                                    Protected
                                                </span>
                                            )}
                                            {hasChanged && !change.isProtected && (
                                                <span className="text-xs bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded">
                                                    Modified
                                                </span>
                                            )}
                                        </label>
                                        <span className="text-sm">
                                            {change.unit === '$' && '$'}
                                            {change.newValue.toLocaleString()}
                                            {change.unit === '%' && '%'}
                                            {change.unit === 'points' && ' pts'}
                                            {change.unit === 'months' && ' mo'}
                                        </span>
                                    </div>

                                    {change.isProtected ? (
                                        <div className="text-xs text-red-400/80 bg-red-500/10 p-3 rounded-lg">
                                            ⚠️ Protected characteristics cannot be adjusted. This ensures fair lending compliance.
                                        </div>
                                    ) : (
                                        <>
                                            <input
                                                type="range"
                                                min={change.min}
                                                max={change.max}
                                                step={change.step}
                                                value={change.newValue}
                                                onChange={(e) => updateChange(globalIndex, parseInt(e.target.value))}
                                                className={`w-full h-2 rounded-lg appearance-none cursor-pointer ${hasChanged
                                                    ? 'bg-purple-500/30 accent-purple-500'
                                                    : 'bg-white/10 accent-primary-500'
                                                    }`}
                                            />
                                            <div className="flex justify-between text-xs text-white/40 mt-1">
                                                <span>{change.unit === '$' ? '$' : ''}{change.min.toLocaleString()}{change.unit === '%' ? '%' : ''}</span>
                                                {hasChanged && (
                                                    <span className="text-purple-300">
                                                        was: {change.unit === '$' ? '$' : ''}{change.currentValue.toLocaleString()}{change.unit === '%' ? '%' : ''}
                                                    </span>
                                                )}
                                                <span>{change.unit === '$' ? '$' : ''}{change.max.toLocaleString()}{change.unit === '%' ? '%' : ''}</span>
                                            </div>
                                        </>
                                    )}
                                </div>
                            );
                        })}
                    </div>

                    <div className="mt-8 space-y-3">
                        <button
                            onClick={runSimulation}
                            disabled={!hasChanges || isSimulating}
                            className="btn-primary w-full disabled:opacity-50"
                        >
                            {isSimulating ? (
                                <span className="flex items-center justify-center gap-2">
                                    <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                                    Simulating...
                                </span>
                            ) : (
                                '🧪 Run Simulation'
                            )}
                        </button>
                        {!hasChanges && (
                            <p className="text-xs text-white/40 text-center">
                                Adjust a slider to see potential impact
                            </p>
                        )}
                    </div>
                </div>

                {/* Results */}
                <div className="glass-card p-6">
                    <h2 className="text-lg font-semibold mb-6">Projected Impact</h2>

                    {error && (
                        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6">
                            <p className="text-red-400 text-sm">{error}</p>
                        </div>
                    )}

                    {result ? (
                        <div className="space-y-6">
                            {/* Plain English Summary */}
                            {buildSummaryData() && (
                                <PlainEnglishSummary
                                    data={buildSummaryData()!}
                                    detailed={false}
                                />
                            )}

                            {/* Confidence Breakdown */}
                            <ConfidenceBreakdown
                                overall={result.confidence === 'high' ? 85 : result.confidence === 'medium' ? 65 : 45}
                                factors={changedFields.map(cf => ({
                                    name: cf.label,
                                    confidence: Math.min(95, 60 + Math.abs(cf.newValue - cf.currentValue) / cf.max * 40),
                                    source: 'Simulation',
                                    weight: 1 / changedFields.length
                                }))}
                                showDetails={true}
                            />

                            {/* Status Changes */}
                            {result.status_changes.length > 0 ? (
                                <div>
                                    <h3 className="text-sm font-medium text-white/70 mb-3">Program Status Changes</h3>
                                    <div className="space-y-2">
                                        {result.status_changes.map((change, i) => (
                                            <div key={i} className="bg-white/5 rounded-lg p-3 flex items-center justify-between">
                                                <span>{change.program_name}</span>
                                                <div className="flex items-center gap-2 text-sm">
                                                    <span className={`px-2 py-0.5 rounded ${change.old_status === 'eligible' ? 'bg-green-500/20 text-green-400' :
                                                        change.old_status === 'refer' ? 'bg-yellow-500/20 text-yellow-400' :
                                                            'bg-red-500/20 text-red-400'
                                                        }`}>
                                                        {change.old_status}
                                                    </span>
                                                    <span className="text-white/40">→</span>
                                                    <span className={`px-2 py-0.5 rounded ${change.new_status === 'eligible' ? 'bg-green-500/20 text-green-400' :
                                                        change.new_status === 'refer' ? 'bg-yellow-500/20 text-yellow-400' :
                                                            'bg-red-500/20 text-red-400'
                                                        }`}>
                                                        {change.new_status}
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ) : (
                                <div className="text-center py-4 text-white/60 bg-white/5 rounded-lg">
                                    <p>No status changes projected</p>
                                    <p className="text-sm mt-1">Try larger adjustments</p>
                                </div>
                            )}

                            {/* Projected Outcomes */}
                            {result.projected_outcomes && (
                                <div className="grid grid-cols-3 gap-3">
                                    <div className="bg-green-500/10 rounded-lg p-3 text-center">
                                        <p className="text-2xl font-bold text-green-400">
                                            +{result.projected_outcomes.programs_unlocked}
                                        </p>
                                        <p className="text-xs text-white/50">Programs Unlocked</p>
                                    </div>
                                    {result.projected_outcomes.rate_improvement && (
                                        <div className="bg-blue-500/10 rounded-lg p-3 text-center">
                                            <p className="text-2xl font-bold text-blue-400">
                                                {result.projected_outcomes.rate_improvement}
                                            </p>
                                            <p className="text-xs text-white/50">Rate Improvement</p>
                                        </div>
                                    )}
                                    {result.projected_outcomes.approval_lift && (
                                        <div className="bg-purple-500/10 rounded-lg p-3 text-center">
                                            <p className="text-2xl font-bold text-purple-400">
                                                {result.projected_outcomes.approval_lift}
                                            </p>
                                            <p className="text-xs text-white/50">Approval Lift</p>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Disclaimer */}
                            <p className="text-xs text-white/40 border-t border-white/10 pt-4">
                                ⚠️ This is an estimate based on hypothetical changes. Actual eligibility may vary based on lender criteria and credit bureau data.
                            </p>
                        </div>
                    ) : (
                        <div className="text-center py-12 text-white/50">
                            <div className="text-6xl mb-4">🔮</div>
                            <p className="text-lg">Ready to explore possibilities</p>
                            <p className="text-sm mt-2 text-white/40">
                                Adjust the sliders on the left and run a simulation<br />
                                to see how changes could affect your options
                            </p>
                            <div className="mt-6 text-left max-w-xs mx-auto">
                                <p className="text-white/60 text-sm mb-2">Quick tips:</p>
                                <ul className="text-white/40 text-xs space-y-1">
                                    <li>• Lowering credit utilization often has big impact</li>
                                    <li>• Paying down debt improves DTI ratio</li>
                                    <li>• Income increases expand your options</li>
                                </ul>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

