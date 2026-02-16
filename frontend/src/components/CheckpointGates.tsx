import { useState, useEffect } from 'react';

interface CheckpointGate {
    name: string;
    status: 'passed' | 'pending' | 'blocked';
    blocking_reason: string | null;
}

interface CheckpointGatesProps {
    caseId: string;
}

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

export default function CheckpointGates({ caseId }: CheckpointGatesProps) {
    const [gates, setGates] = useState<CheckpointGate[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchGates();
    }, [caseId]);

    const fetchGates = async () => {
        try {
            const res = await fetch(`${API_URL}/cases/${caseId}/agents/checkpoints`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('goatcrd_token')}` },
            });
            if (res.ok) {
                const data = await res.json();
                setGates(data.gates || []);
            }
        } catch {
            // Fallback for demo
            setGates([
                { name: 'Pre-Triage', status: 'passed', blocking_reason: null },
                { name: 'Pre-Explanation', status: 'pending', blocking_reason: 'Scenarios not yet generated' },
                { name: 'Pre-Export', status: 'blocked', blocking_reason: 'Pre-Explanation gate not passed' },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const getGateIcon = (status: string) => {
        switch (status) {
            case 'passed': return '✅';
            case 'pending': return '🕐';
            case 'blocked': return '🚫';
            default: return '⚪';
        }
    };

    const getGateColor = (status: string) => {
        switch (status) {
            case 'passed': return 'border-emerald-500/30 bg-emerald-500/5';
            case 'pending': return 'border-amber-500/30 bg-amber-500/5';
            case 'blocked': return 'border-red-500/30 bg-red-500/5';
            default: return 'border-white/10 bg-white/5';
        }
    };

    const getConnectorColor = (status: string) => {
        switch (status) {
            case 'passed': return 'bg-emerald-500';
            case 'pending': return 'bg-amber-500/50';
            default: return 'bg-white/20';
        }
    };

    if (loading) {
        return (
            <div className="glass rounded-xl p-6 border border-white/10 animate-pulse">
                <div className="h-6 bg-white/10 rounded w-48 mb-4" />
                <div className="flex gap-4">
                    {[1, 2, 3].map(i => <div key={i} className="h-20 bg-white/5 rounded-lg flex-1" />)}
                </div>
            </div>
        );
    }

    return (
        <div className="glass rounded-xl p-6 border border-white/10">
            <div className="flex items-center gap-3 mb-5">
                <span className="text-xl">🚦</span>
                <h3 className="text-lg font-semibold text-white">Checkpoint Gates</h3>
                <span className="text-xs text-white/50 bg-white/5 px-2 py-0.5 rounded-full">
                    {gates.filter(g => g.status === 'passed').length}/{gates.length} passed
                </span>
            </div>

            <div className="flex items-start gap-2">
                {gates.map((gate, i) => (
                    <div key={gate.name} className="flex items-start flex-1">
                        <div className={`rounded-lg border p-4 flex-1 ${getGateColor(gate.status)}`}>
                            <div className="flex items-center gap-2 mb-2">
                                <span className="text-lg">{getGateIcon(gate.status)}</span>
                                <span className="text-sm font-medium text-white">{gate.name}</span>
                            </div>
                            <span className={`text-xs capitalize ${gate.status === 'passed' ? 'text-emerald-400' :
                                    gate.status === 'pending' ? 'text-amber-400' :
                                        'text-red-400'
                                }`}>
                                {gate.status}
                            </span>
                            {gate.blocking_reason && (
                                <p className="text-xs text-white/50 mt-1">{gate.blocking_reason}</p>
                            )}
                        </div>
                        {i < gates.length - 1 && (
                            <div className="flex items-center pt-6 px-1">
                                <div className={`w-4 h-0.5 ${getConnectorColor(gate.status)}`} />
                                <span className="text-white/20">›</span>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
