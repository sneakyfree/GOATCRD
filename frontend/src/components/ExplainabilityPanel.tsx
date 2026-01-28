import { useState } from 'react';

type ExplanationLayer = 'summary' | 'factors' | 'rules' | 'data';

interface ExplanationData {
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
        threshold?: string;
        actual_value?: string;
        explanation: string;
    }>;
    data: Array<{
        field: string;
        value: string;
        source: string;
        confidence: number;
    }>;
}

interface ExplainabilityPanelProps {
    scenarioId: string;
    programName: string;
    explanation: ExplanationData;
    onClose?: () => void;
}

/**
 * ExplainabilityPanel Component
 * 
 * 4-Layer explanation interface:
 * 1. Summary - Plain English "why"
 * 2. Factors - Key contributing factors
 * 3. Rules - Specific rules applied
 * 4. Data - Source data with provenance
 */
export function ExplainabilityPanel({
    scenarioId,
    programName,
    explanation,
    onClose
}: ExplainabilityPanelProps) {
    const [activeLayer, setActiveLayer] = useState<ExplanationLayer>('summary');

    const layers: { id: ExplanationLayer; label: string; icon: string }[] = [
        { id: 'summary', label: 'Summary', icon: '📝' },
        { id: 'factors', label: 'Factors', icon: '⚖️' },
        { id: 'rules', label: 'Rules', icon: '📋' },
        { id: 'data', label: 'Data', icon: '🔍' }
    ];

    const getImpactColor = (impact: string) => {
        switch (impact) {
            case 'positive': return 'text-green-400 bg-green-500/20';
            case 'negative': return 'text-red-400 bg-red-500/20';
            default: return 'text-gray-400 bg-gray-500/20';
        }
    };

    const getImpactIcon = (impact: string) => {
        switch (impact) {
            case 'positive': return '↑';
            case 'negative': return '↓';
            default: return '→';
        }
    };

    return (
        <div className="glass rounded-xl overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/10 bg-white/5">
                <div>
                    <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                        <span>💡</span>
                        Why This Result?
                    </h2>
                    <p className="text-white/50 text-sm">{programName}</p>
                </div>
                {onClose && (
                    <button onClick={onClose} className="text-white/50 hover:text-white p-2">
                        ✕
                    </button>
                )}
            </div>

            {/* Layer Tabs */}
            <div className="flex border-b border-white/10">
                {layers.map(layer => (
                    <button
                        key={layer.id}
                        onClick={() => setActiveLayer(layer.id)}
                        className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${activeLayer === layer.id
                                ? 'bg-purple-500/20 text-purple-300 border-b-2 border-purple-500'
                                : 'text-white/60 hover:bg-white/5'
                            }`}
                    >
                        <span className="mr-2">{layer.icon}</span>
                        {layer.label}
                    </button>
                ))}
            </div>

            {/* Layer Content */}
            <div className="p-6">
                {/* Summary Layer */}
                {activeLayer === 'summary' && (
                    <div className="space-y-6">
                        <div className={`p-4 rounded-lg ${explanation.summary.outcome === 'ELIGIBLE'
                                ? 'bg-green-500/10 border border-green-500/30'
                                : explanation.summary.outcome === 'REFER'
                                    ? 'bg-yellow-500/10 border border-yellow-500/30'
                                    : 'bg-red-500/10 border border-red-500/30'
                            }`}>
                            <div className="flex items-center justify-between mb-3">
                                <span className="text-white font-medium">Outcome</span>
                                <span className={`px-3 py-1 rounded-full text-sm ${explanation.summary.outcome === 'ELIGIBLE' ? 'bg-green-500/30 text-green-300' :
                                        explanation.summary.outcome === 'REFER' ? 'bg-yellow-500/30 text-yellow-300' :
                                            'bg-red-500/30 text-red-300'
                                    }`}>
                                    {explanation.summary.outcome}
                                </span>
                            </div>
                            <p className="text-white/80">{explanation.summary.plain_english}</p>
                        </div>

                        <div className="bg-white/5 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-white/60">Confidence Level</span>
                                <span className="text-white font-bold">{explanation.summary.confidence}%</span>
                            </div>
                            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                <div
                                    className={`h-full rounded-full ${explanation.summary.confidence >= 80 ? 'bg-green-500' :
                                            explanation.summary.confidence >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                                        }`}
                                    style={{ width: `${explanation.summary.confidence}%` }}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {/* Factors Layer */}
                {activeLayer === 'factors' && (
                    <div className="space-y-4">
                        {explanation.factors.map((factor, i) => (
                            <div key={i} className="bg-white/5 rounded-lg p-4">
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <span className={`w-6 h-6 rounded-full flex items-center justify-center text-sm ${getImpactColor(factor.impact)}`}>
                                            {getImpactIcon(factor.impact)}
                                        </span>
                                        <span className="text-white font-medium">{factor.name}</span>
                                    </div>
                                    <span className="text-white/60 text-sm">Weight: {(factor.weight * 100).toFixed(0)}%</span>
                                </div>
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-white/50">{factor.description}</span>
                                    <span className="text-white">{factor.value}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Rules Layer */}
                {activeLayer === 'rules' && (
                    <div className="space-y-3">
                        {explanation.rules.map((rule, i) => (
                            <div
                                key={i}
                                className={`rounded-lg p-4 border ${rule.passed
                                        ? 'bg-green-500/5 border-green-500/20'
                                        : 'bg-red-500/5 border-red-500/20'
                                    }`}
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <span className={rule.passed ? 'text-green-400' : 'text-red-400'}>
                                            {rule.passed ? '✓' : '✕'}
                                        </span>
                                        <span className="text-white font-medium">{rule.rule_name}</span>
                                    </div>
                                    <span className="text-white/40 text-xs font-mono">{rule.rule_id}</span>
                                </div>
                                <p className="text-white/60 text-sm">{rule.explanation}</p>
                                {(rule.threshold || rule.actual_value) && (
                                    <div className="flex gap-4 mt-2 text-xs">
                                        {rule.threshold && (
                                            <span className="text-white/40">Threshold: {rule.threshold}</span>
                                        )}
                                        {rule.actual_value && (
                                            <span className="text-white/40">Actual: {rule.actual_value}</span>
                                        )}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {/* Data Layer */}
                {activeLayer === 'data' && (
                    <div className="space-y-2">
                        <table className="w-full">
                            <thead>
                                <tr className="text-left text-white/50 text-sm">
                                    <th className="pb-3">Field</th>
                                    <th className="pb-3">Value</th>
                                    <th className="pb-3">Source</th>
                                    <th className="pb-3">Confidence</th>
                                </tr>
                            </thead>
                            <tbody>
                                {explanation.data.map((item, i) => (
                                    <tr key={i} className="border-t border-white/5">
                                        <td className="py-3 text-white/80">{item.field}</td>
                                        <td className="py-3 text-white">{item.value}</td>
                                        <td className="py-3">
                                            <span className={`text-xs px-2 py-0.5 rounded-full ${item.source.includes('verified') ? 'bg-green-500/20 text-green-300' :
                                                    item.source.includes('stated') ? 'bg-yellow-500/20 text-yellow-300' :
                                                        'bg-white/10 text-white/60'
                                                }`}>
                                                {item.source}
                                            </span>
                                        </td>
                                        <td className="py-3 text-white/60">{item.confidence}%</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="px-6 py-4 bg-white/5 border-t border-white/10">
                <p className="text-white/40 text-xs text-center">
                    Scenario ID: {scenarioId} • This explanation is for informational purposes only
                </p>
            </div>
        </div>
    );
}

export default ExplainabilityPanel;
