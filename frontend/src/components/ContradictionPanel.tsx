import { useState } from 'react';

interface Contradiction {
    id: string;
    field_a: string;
    field_b: string;
    value_a: string;
    value_b: string;
    severity: 'low' | 'medium' | 'high';
    suggested_resolution: string;
}

interface ContradictionPanelProps {
    caseId: string;
    onResolved?: () => void;
}

export default function ContradictionPanel({ caseId: _caseId, onResolved }: ContradictionPanelProps) {
    const [contradictions] = useState<Contradiction[]>([
        {
            id: '1',
            field_a: 'Stated Income (Ch.3)',
            field_b: 'Bank Deposits (Alt Data)',
            value_a: '$72,000 / year',
            value_b: '$68,400 avg deposits',
            severity: 'medium',
            suggested_resolution: 'Use bank-verified income ($68,400). Variance within 5% tolerance.',
        },
        {
            id: '2',
            field_a: 'Employment Start (Ch.3)',
            field_b: 'Payroll Records (Alt Data)',
            value_a: 'Jan 2023',
            value_b: 'Mar 2023',
            severity: 'low',
            suggested_resolution: 'Accept payroll records as authoritative. 2-month discrepancy.',
        },
    ]);
    const [resolving, setResolving] = useState<string | null>(null);
    const [resolved, setResolved] = useState<Set<string>>(new Set());

    const handleAcceptSuggestion = (id: string) => {
        setResolving(id);
        setTimeout(() => {
            setResolved(prev => new Set(prev).add(id));
            setResolving(null);
            onResolved?.();
        }, 600);
    };

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'high': return 'text-red-400 bg-red-500/10 border-red-500/30';
            case 'medium': return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
            case 'low': return 'text-blue-400 bg-blue-500/10 border-blue-500/30';
            default: return 'text-white/60 bg-white/5 border-white/10';
        }
    };

    const getSeverityIcon = (severity: string) => {
        switch (severity) {
            case 'high': return '🔴';
            case 'medium': return '🟡';
            case 'low': return '🔵';
            default: return '⚪';
        }
    };

    const unresolvedCount = contradictions.filter(c => !resolved.has(c.id)).length;

    if (contradictions.length === 0) return null;

    return (
        <div className="glass rounded-xl p-6 border border-white/10 mb-6">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <span className="text-2xl">⚠️</span>
                    <div>
                        <h3 className="text-lg font-semibold text-white">Cross-Source Contradictions</h3>
                        <p className="text-white/60 text-sm">
                            {unresolvedCount === 0
                                ? 'All contradictions resolved ✓'
                                : `${unresolvedCount} conflict${unresolvedCount > 1 ? 's' : ''} detected between intake data and verified sources`
                            }
                        </p>
                    </div>
                </div>
                {unresolvedCount === 0 && (
                    <span className="text-emerald-400 text-sm font-medium bg-emerald-500/10 px-3 py-1 rounded-full">
                        ✓ All Clear
                    </span>
                )}
            </div>

            <div className="space-y-3">
                {contradictions.map(c => (
                    <div
                        key={c.id}
                        className={`rounded-lg border p-4 transition-all duration-300 ${resolved.has(c.id)
                            ? 'bg-emerald-500/5 border-emerald-500/20 opacity-60'
                            : getSeverityColor(c.severity)
                            }`}
                    >
                        <div className="flex items-start justify-between gap-4">
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-2">
                                    <span>{getSeverityIcon(c.severity)}</span>
                                    <span className="text-xs font-medium uppercase tracking-wider text-white/50">
                                        {c.severity} severity
                                    </span>
                                    {resolved.has(c.id) && (
                                        <span className="text-emerald-400 text-xs">✓ Resolved</span>
                                    )}
                                </div>
                                <div className="grid grid-cols-2 gap-3 mb-3">
                                    <div className="text-sm">
                                        <span className="text-white/50 text-xs block mb-1">{c.field_a}</span>
                                        <span className="text-white font-mono">{c.value_a}</span>
                                    </div>
                                    <div className="text-sm">
                                        <span className="text-white/50 text-xs block mb-1">{c.field_b}</span>
                                        <span className="text-white font-mono">{c.value_b}</span>
                                    </div>
                                </div>
                                <p className="text-sm text-white/70 italic">
                                    💡 {c.suggested_resolution}
                                </p>
                            </div>
                            {!resolved.has(c.id) && (
                                <button
                                    onClick={() => handleAcceptSuggestion(c.id)}
                                    disabled={resolving === c.id}
                                    className="btn-primary text-xs shrink-0 px-3 py-1.5"
                                >
                                    {resolving === c.id ? 'Resolving…' : 'Accept'}
                                </button>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
