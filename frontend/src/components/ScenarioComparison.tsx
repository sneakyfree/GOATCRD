import { useState } from 'react';

interface Scenario {
    id: string;
    program_name: string;
    status: 'ELIGIBLE' | 'REFER' | 'NOT_ELIGIBLE';
    interest_rate?: number;
    monthly_payment?: number;
    max_loan_amount?: number;
    term_months?: number;
    confidence: number;
    closing_time_days?: number;
    total_cost?: number;
    reason_codes?: string[];
}

interface ScenarioComparisonProps {
    scenarios: Scenario[];
    onSelect?: (scenarioId: string) => void;
    onRemove?: (scenarioId: string) => void;
}

/**
 * ScenarioComparison Component
 * 
 * Side-by-side comparison of up to 3 scenarios
 * with visual indicators for best values.
 */
export function ScenarioComparison({
    scenarios,
    onSelect,
    onRemove
}: ScenarioComparisonProps) {
    const [highlightBest, setHighlightBest] = useState(true);

    const formatCurrency = (amount?: number) => {
        if (amount === undefined) return '—';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0
        }).format(amount);
    };

    const formatPercent = (value?: number) => {
        if (value === undefined) return '—';
        return `${value.toFixed(2)}%`;
    };

    const getBestValue = (
        key: keyof Scenario,
        preferLower: boolean = true
    ): string | undefined => {
        const values = scenarios
            .filter(s => s.status === 'ELIGIBLE' && s[key] !== undefined)
            .map(s => ({ id: s.id, value: s[key] as number }));

        if (values.length === 0) return undefined;

        const best = preferLower
            ? values.reduce((a, b) => a.value < b.value ? a : b)
            : values.reduce((a, b) => a.value > b.value ? a : b);

        return best.id;
    };

    const comparisonRows = [
        { label: 'Status', key: 'status' as keyof Scenario },
        { label: 'Interest Rate', key: 'interest_rate' as keyof Scenario, format: formatPercent, best: getBestValue('interest_rate', true) },
        { label: 'Monthly Payment', key: 'monthly_payment' as keyof Scenario, format: formatCurrency, best: getBestValue('monthly_payment', true) },
        { label: 'Max Amount', key: 'max_loan_amount' as keyof Scenario, format: formatCurrency, best: getBestValue('max_loan_amount', false) },
        { label: 'Term', key: 'term_months' as keyof Scenario, format: (v?: number) => v ? `${v} months` : '—' },
        { label: 'Closing Time', key: 'closing_time_days' as keyof Scenario, format: (v?: number) => v ? `${v} days` : '—', best: getBestValue('closing_time_days', true) },
        { label: 'Total Cost', key: 'total_cost' as keyof Scenario, format: formatCurrency, best: getBestValue('total_cost', true) },
        { label: 'Confidence', key: 'confidence' as keyof Scenario, format: (v?: number) => v ? `${v}%` : '—', best: getBestValue('confidence', false) }
    ];

    const getStatusStyles = (status: string) => {
        switch (status) {
            case 'ELIGIBLE': return 'bg-green-500/20 text-green-300';
            case 'REFER': return 'bg-yellow-500/20 text-yellow-300';
            case 'NOT_ELIGIBLE': return 'bg-red-500/20 text-red-300';
            default: return 'bg-white/10 text-white/60';
        }
    };

    if (scenarios.length === 0) {
        return (
            <div className="glass rounded-xl p-8 text-center">
                <div className="text-5xl mb-4">📊</div>
                <p className="text-white/60">Select scenarios to compare</p>
                <p className="text-white/40 text-sm mt-2">Choose up to 3 scenarios from the list</p>
            </div>
        );
    }

    return (
        <div className="glass rounded-xl overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/10">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                    <span>📊</span>
                    Compare Scenarios
                </h2>
                <label className="flex items-center gap-2 text-sm">
                    <input
                        type="checkbox"
                        checked={highlightBest}
                        onChange={(e) => setHighlightBest(e.target.checked)}
                        className="rounded"
                    />
                    <span className="text-white/60">Highlight best values</span>
                </label>
            </div>

            {/* Comparison Table */}
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-white/10">
                            <th className="text-left p-4 text-white/50 font-medium w-40">Attribute</th>
                            {scenarios.map(scenario => (
                                <th key={scenario.id} className="text-center p-4 min-w-[180px]">
                                    <div className="flex flex-col items-center gap-2">
                                        <span className="text-white font-medium">{scenario.program_name}</span>
                                        {onRemove && (
                                            <button
                                                onClick={() => onRemove(scenario.id)}
                                                className="text-white/40 hover:text-red-400 text-xs"
                                            >
                                                Remove
                                            </button>
                                        )}
                                    </div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {comparisonRows.map((row, i) => (
                            <tr key={i} className="border-b border-white/5">
                                <td className="p-4 text-white/60">{row.label}</td>
                                {scenarios.map(scenario => {
                                    const value = scenario[row.key];
                                    const isBest = highlightBest && row.best === scenario.id;
                                    const displayValue = row.key === 'status'
                                        ? value
                                        : row.format
                                            ? row.format(value as number | undefined)
                                            : value?.toString() || '—';

                                    return (
                                        <td key={scenario.id} className="p-4 text-center">
                                            {row.key === 'status' ? (
                                                <span className={`px-3 py-1 rounded-full text-sm ${getStatusStyles(value as string)}`}>
                                                    {value}
                                                </span>
                                            ) : (
                                                <span className={`${isBest ? 'text-green-400 font-bold' : 'text-white'}`}>
                                                    {isBest && '⭐ '}
                                                    {displayValue}
                                                </span>
                                            )}
                                        </td>
                                    );
                                })}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Reason Codes */}
            <div className="p-4 border-t border-white/10">
                <h3 className="text-white/60 text-sm mb-3">Considerations</h3>
                <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${scenarios.length}, 1fr)` }}>
                    {scenarios.map(scenario => (
                        <div key={scenario.id} className="text-center">
                            {scenario.reason_codes?.length ? (
                                <div className="flex flex-wrap gap-1 justify-center">
                                    {scenario.reason_codes.slice(0, 3).map((code, i) => (
                                        <span key={i} className="bg-white/10 text-white/60 text-xs px-2 py-0.5 rounded">
                                            {code}
                                        </span>
                                    ))}
                                </div>
                            ) : (
                                <span className="text-white/30 text-sm">No considerations</span>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Actions */}
            {onSelect && (
                <div className="p-4 bg-white/5 border-t border-white/10">
                    <div className="flex gap-4">
                        {scenarios.filter(s => s.status === 'ELIGIBLE').map(scenario => (
                            <button
                                key={scenario.id}
                                onClick={() => onSelect(scenario.id)}
                                className="flex-1 bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded-lg transition-colors"
                            >
                                Select {scenario.program_name}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default ScenarioComparison;
