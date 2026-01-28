import { useState } from 'react';

// Types
interface Ruleset {
    id: string;
    name: string;
    description: string;
    version: number;
    status: 'active' | 'draft' | 'deprecated';
    program_ids: string[];
    rules: Rule[];
    created_at: string;
    updated_at: string;
    created_by: string;
}

interface Rule {
    id: string;
    field: string;
    operator: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'not_in' | 'between';
    value: string | number | boolean | string[] | [number, number];
    action: 'eligible' | 'refer' | 'not_eligible';
    reason_code?: string;
    priority: number;
}

// Mock data
const MOCK_RULESETS: Ruleset[] = [
    {
        id: '1',
        name: 'Standard Credit Card Rules',
        description: 'Default eligibility rules for credit card products',
        version: 4,
        status: 'active',
        program_ids: ['1'],
        rules: [
            { id: 'r1', field: 'credit_score', operator: 'gte', value: 700, action: 'eligible', priority: 1 },
            { id: 'r2', field: 'credit_score', operator: 'between', value: [650, 699], action: 'refer', reason_code: 'RC002', priority: 2 },
            { id: 'r3', field: 'credit_score', operator: 'lt', value: 650, action: 'not_eligible', reason_code: 'RC002', priority: 3 },
            { id: 'r4', field: 'dti', operator: 'lte', value: 0.40, action: 'eligible', priority: 4 },
            { id: 'r5', field: 'dti', operator: 'gt', value: 0.40, action: 'not_eligible', reason_code: 'RC003', priority: 5 },
            { id: 'r6', field: 'bankruptcy_recent', operator: 'eq', value: true, action: 'not_eligible', reason_code: 'RC007', priority: 6 },
        ],
        created_at: '2024-01-15T10:00:00Z',
        updated_at: '2025-01-20T14:30:00Z',
        created_by: 'admin@goatcrd.com',
    },
    {
        id: '2',
        name: 'Personal Loan - Subprime',
        description: 'Rules for subprime personal loan products',
        version: 2,
        status: 'active',
        program_ids: ['2'],
        rules: [
            { id: 'r1', field: 'credit_score', operator: 'gte', value: 580, action: 'eligible', priority: 1 },
            { id: 'r2', field: 'income_verified', operator: 'eq', value: true, action: 'eligible', priority: 2 },
            { id: 'r3', field: 'income_verified', operator: 'eq', value: false, action: 'refer', reason_code: 'RC005', priority: 3 },
        ],
        created_at: '2024-06-01T09:00:00Z',
        updated_at: '2024-12-15T11:00:00Z',
        created_by: 'admin@goatcrd.com',
    },
    {
        id: '3',
        name: 'Mortgage FHA Guidelines',
        description: 'FHA mortgage eligibility rules',
        version: 1,
        status: 'draft',
        program_ids: [],
        rules: [
            { id: 'r1', field: 'credit_score', operator: 'gte', value: 580, action: 'eligible', priority: 1 },
            { id: 'r2', field: 'dti', operator: 'lte', value: 0.43, action: 'eligible', priority: 2 },
        ],
        created_at: '2026-01-10T08:00:00Z',
        updated_at: '2026-01-10T08:00:00Z',
        created_by: 'admin@goatcrd.com',
    },
];

const OPERATORS = [
    { value: 'eq', label: '= (equals)', symbol: '=' },
    { value: 'neq', label: '≠ (not equals)', symbol: '≠' },
    { value: 'gt', label: '> (greater than)', symbol: '>' },
    { value: 'gte', label: '≥ (greater or equal)', symbol: '≥' },
    { value: 'lt', label: '< (less than)', symbol: '<' },
    { value: 'lte', label: '≤ (less or equal)', symbol: '≤' },
    { value: 'in', label: 'IN (one of)', symbol: '∈' },
    { value: 'not_in', label: 'NOT IN', symbol: '∉' },
    { value: 'between', label: 'BETWEEN', symbol: '↔' },
];

const FIELDS = [
    { value: 'credit_score', label: 'Credit Score', type: 'number' },
    { value: 'dti', label: 'Debt-to-Income Ratio', type: 'number' },
    { value: 'income', label: 'Annual Income', type: 'number' },
    { value: 'income_verified', label: 'Income Verified', type: 'boolean' },
    { value: 'employment_months', label: 'Employment Duration (months)', type: 'number' },
    { value: 'bankruptcy_recent', label: 'Recent Bankruptcy', type: 'boolean' },
    { value: 'delinquency_months', label: 'Months Since Delinquency', type: 'number' },
    { value: 'state', label: 'State', type: 'string' },
    { value: 'loan_amount', label: 'Requested Amount', type: 'number' },
];

const ACTIONS = [
    { value: 'eligible', label: 'ELIGIBLE', color: 'text-green-400 bg-green-500/20' },
    { value: 'refer', label: 'REFER', color: 'text-yellow-400 bg-yellow-500/20' },
    { value: 'not_eligible', label: 'NOT ELIGIBLE', color: 'text-red-400 bg-red-500/20' },
];

export default function AdminRulesetsPage() {
    const [rulesets, setRulesets] = useState<Ruleset[]>(MOCK_RULESETS);
    const [selectedRuleset, setSelectedRuleset] = useState<Ruleset | null>(null);
    const [showEditor, setShowEditor] = useState(false);
    const [showDiff, setShowDiff] = useState(false);

    const handleCreateRuleset = () => {
        const newRuleset: Ruleset = {
            id: Date.now().toString(),
            name: 'New Ruleset',
            description: '',
            version: 1,
            status: 'draft',
            program_ids: [],
            rules: [],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            created_by: 'admin@goatcrd.com',
        };
        setRulesets(prev => [newRuleset, ...prev]);
        setSelectedRuleset(newRuleset);
        setShowEditor(true);
    };

    const handleSaveRuleset = (updatedRuleset: Ruleset) => {
        setRulesets(prev => prev.map(r =>
            r.id === updatedRuleset.id
                ? { ...updatedRuleset, version: r.version + 1, updated_at: new Date().toISOString() }
                : r
        ));
        setShowEditor(false);
    };

    const handleActivate = (ruleset: Ruleset) => {
        setRulesets(prev => prev.map(r =>
            r.id === ruleset.id
                ? { ...r, status: 'active' as const, updated_at: new Date().toISOString() }
                : r
        ));
    };

    const getStatusBadge = (status: Ruleset['status']) => {
        const styles = {
            active: 'bg-green-500/20 text-green-400 border-green-500/30',
            deprecated: 'bg-red-500/20 text-red-400 border-red-500/30',
            draft: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
        };
        return (
            <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${styles[status]}`}>
                {status.toUpperCase()}
            </span>
        );
    };

    const formatRuleValue = (rule: Rule) => {
        if (Array.isArray(rule.value)) {
            if (rule.operator === 'between') {
                return `${rule.value[0]} - ${rule.value[1]}`;
            }
            return rule.value.join(', ');
        }
        if (typeof rule.value === 'boolean') {
            return rule.value ? 'Yes' : 'No';
        }
        return String(rule.value);
    };

    return (
        <div className="min-h-screen bg-slate-900 text-white">
            {/* Header */}
            <div className="bg-slate-800/50 border-b border-slate-700 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-2xl font-bold">Ruleset Governance</h1>
                            <p className="text-slate-400 text-sm">Manage eligibility rules with version control</p>
                        </div>
                        <button
                            onClick={handleCreateRuleset}
                            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
                        >
                            <span>+</span> New Ruleset
                        </button>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 py-6">
                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold">{rulesets.length}</div>
                        <div className="text-slate-400 text-sm">Total Rulesets</div>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold text-green-400">
                            {rulesets.filter(r => r.status === 'active').length}
                        </div>
                        <div className="text-slate-400 text-sm">Active</div>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold text-yellow-400">
                            {rulesets.filter(r => r.status === 'draft').length}
                        </div>
                        <div className="text-slate-400 text-sm">Drafts</div>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold text-blue-400">
                            {rulesets.reduce((acc, r) => acc + r.rules.length, 0)}
                        </div>
                        <div className="text-slate-400 text-sm">Total Rules</div>
                    </div>
                </div>

                {/* Ruleset List */}
                <div className="space-y-4">
                    {rulesets.map(ruleset => (
                        <div
                            key={ruleset.id}
                            className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden"
                        >
                            {/* Ruleset Header */}
                            <div className="p-4 flex items-start justify-between">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <h3 className="font-semibold text-lg">{ruleset.name}</h3>
                                        {getStatusBadge(ruleset.status)}
                                        <span className="text-slate-500 text-sm">v{ruleset.version}</span>
                                    </div>
                                    <p className="text-slate-400 text-sm mt-1">{ruleset.description || 'No description'}</p>
                                    <p className="text-slate-500 text-xs mt-2">
                                        {ruleset.rules.length} rules • Updated {new Date(ruleset.updated_at).toLocaleDateString()}
                                    </p>
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => { setSelectedRuleset(ruleset); setShowEditor(true); }}
                                        className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
                                        title="Edit"
                                    >
                                        ✏️
                                    </button>
                                    <button
                                        onClick={() => { setSelectedRuleset(ruleset); setShowDiff(true); }}
                                        className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
                                        title="Version Diff"
                                    >
                                        📊
                                    </button>
                                    {ruleset.status === 'draft' && (
                                        <button
                                            onClick={() => handleActivate(ruleset)}
                                            className="px-3 py-2 bg-green-600/20 hover:bg-green-600/40 text-green-400 rounded-lg transition-colors text-sm"
                                        >
                                            Activate
                                        </button>
                                    )}
                                </div>
                            </div>

                            {/* Rules Preview */}
                            <div className="border-t border-slate-700 bg-slate-900/50">
                                <div className="px-4 py-2 text-xs text-slate-500 font-medium uppercase tracking-wide">
                                    Rules Preview
                                </div>
                                <div className="px-4 pb-4 space-y-2">
                                    {ruleset.rules.slice(0, 3).map(rule => (
                                        <div
                                            key={rule.id}
                                            className="flex items-center gap-3 text-sm bg-slate-800 rounded-lg p-2"
                                        >
                                            <span className="text-slate-400 font-mono">
                                                {FIELDS.find(f => f.value === rule.field)?.label || rule.field}
                                            </span>
                                            <span className="text-blue-400 font-mono">
                                                {OPERATORS.find(o => o.value === rule.operator)?.symbol}
                                            </span>
                                            <span className="text-white font-mono">
                                                {formatRuleValue(rule)}
                                            </span>
                                            <span className="text-slate-500">→</span>
                                            <span className={`px-2 py-0.5 rounded text-xs font-medium ${ACTIONS.find(a => a.value === rule.action)?.color}`}>
                                                {rule.action.toUpperCase()}
                                            </span>
                                            {rule.reason_code && (
                                                <span className="text-slate-500 text-xs">({rule.reason_code})</span>
                                            )}
                                        </div>
                                    ))}
                                    {ruleset.rules.length > 3 && (
                                        <div className="text-slate-500 text-sm pl-2">
                                            +{ruleset.rules.length - 3} more rules...
                                        </div>
                                    )}
                                    {ruleset.rules.length === 0 && (
                                        <div className="text-slate-500 text-sm italic">No rules defined</div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Rule Editor Modal */}
            {showEditor && selectedRuleset && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-slate-800 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                        <div className="sticky top-0 bg-slate-800 p-4 border-b border-slate-700 flex items-center justify-between z-10">
                            <div>
                                <input
                                    type="text"
                                    value={selectedRuleset.name}
                                    onChange={(e) => setSelectedRuleset({ ...selectedRuleset, name: e.target.value })}
                                    className="text-xl font-semibold bg-transparent border-b border-transparent hover:border-slate-600 focus:border-blue-500 outline-none"
                                />
                                <input
                                    type="text"
                                    value={selectedRuleset.description}
                                    onChange={(e) => setSelectedRuleset({ ...selectedRuleset, description: e.target.value })}
                                    placeholder="Add description..."
                                    className="block text-sm text-slate-400 bg-transparent border-b border-transparent hover:border-slate-600 focus:border-blue-500 outline-none mt-1 w-full"
                                />
                            </div>
                            <button
                                onClick={() => setShowEditor(false)}
                                className="p-2 hover:bg-slate-700 rounded-lg"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="p-4">
                            {/* Rules Table */}
                            <div className="space-y-2 mb-4">
                                {selectedRuleset.rules.map((rule, index) => (
                                    <div
                                        key={rule.id}
                                        className="flex items-center gap-2 bg-slate-900 rounded-lg p-3"
                                    >
                                        <span className="text-slate-500 text-sm w-6">{index + 1}.</span>

                                        <select
                                            value={rule.field}
                                            onChange={(e) => {
                                                const updated = { ...rule, field: e.target.value };
                                                setSelectedRuleset({
                                                    ...selectedRuleset,
                                                    rules: selectedRuleset.rules.map(r => r.id === rule.id ? updated : r)
                                                });
                                            }}
                                            className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm flex-1"
                                        >
                                            {FIELDS.map(f => (
                                                <option key={f.value} value={f.value}>{f.label}</option>
                                            ))}
                                        </select>

                                        <select
                                            value={rule.operator}
                                            onChange={(e) => {
                                                const updated = { ...rule, operator: e.target.value as Rule['operator'] };
                                                setSelectedRuleset({
                                                    ...selectedRuleset,
                                                    rules: selectedRuleset.rules.map(r => r.id === rule.id ? updated : r)
                                                });
                                            }}
                                            className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm w-32"
                                        >
                                            {OPERATORS.map(o => (
                                                <option key={o.value} value={o.value}>{o.label}</option>
                                            ))}
                                        </select>

                                        <input
                                            type="text"
                                            value={formatRuleValue(rule)}
                                            onChange={(e) => {
                                                const updated = { ...rule, value: e.target.value };
                                                setSelectedRuleset({
                                                    ...selectedRuleset,
                                                    rules: selectedRuleset.rules.map(r => r.id === rule.id ? updated : r)
                                                });
                                            }}
                                            className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm w-24"
                                        />

                                        <span className="text-slate-500">→</span>

                                        <select
                                            value={rule.action}
                                            onChange={(e) => {
                                                const updated = { ...rule, action: e.target.value as Rule['action'] };
                                                setSelectedRuleset({
                                                    ...selectedRuleset,
                                                    rules: selectedRuleset.rules.map(r => r.id === rule.id ? updated : r)
                                                });
                                            }}
                                            className={`border border-slate-700 rounded px-2 py-1 text-sm w-32 ${ACTIONS.find(a => a.value === rule.action)?.color}`}
                                        >
                                            {ACTIONS.map(a => (
                                                <option key={a.value} value={a.value}>{a.label}</option>
                                            ))}
                                        </select>

                                        <input
                                            type="text"
                                            value={rule.reason_code || ''}
                                            onChange={(e) => {
                                                const updated = { ...rule, reason_code: e.target.value || undefined };
                                                setSelectedRuleset({
                                                    ...selectedRuleset,
                                                    rules: selectedRuleset.rules.map(r => r.id === rule.id ? updated : r)
                                                });
                                            }}
                                            placeholder="RC..."
                                            className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm w-20"
                                        />

                                        <button
                                            onClick={() => {
                                                setSelectedRuleset({
                                                    ...selectedRuleset,
                                                    rules: selectedRuleset.rules.filter(r => r.id !== rule.id)
                                                });
                                            }}
                                            className="p-1 text-red-400 hover:bg-red-500/20 rounded"
                                        >
                                            🗑️
                                        </button>
                                    </div>
                                ))}
                            </div>

                            {/* Add Rule Button */}
                            <button
                                onClick={() => {
                                    const newRule: Rule = {
                                        id: Date.now().toString(),
                                        field: 'credit_score',
                                        operator: 'gte',
                                        value: 650,
                                        action: 'eligible',
                                        priority: selectedRuleset.rules.length + 1,
                                    };
                                    setSelectedRuleset({
                                        ...selectedRuleset,
                                        rules: [...selectedRuleset.rules, newRule]
                                    });
                                }}
                                className="w-full py-3 border-2 border-dashed border-slate-700 rounded-lg text-slate-400 hover:border-blue-500 hover:text-blue-400 transition-colors"
                            >
                                + Add Rule
                            </button>
                        </div>

                        <div className="sticky bottom-0 bg-slate-800 p-4 border-t border-slate-700 flex justify-end gap-3">
                            <button
                                onClick={() => setShowEditor(false)}
                                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => handleSaveRuleset(selectedRuleset)}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium"
                            >
                                Save & Increment Version
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Version Diff Modal */}
            {showDiff && selectedRuleset && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-slate-800 rounded-xl w-full max-w-2xl">
                        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
                            <h2 className="text-xl font-semibold">Version Comparison</h2>
                            <button
                                onClick={() => setShowDiff(false)}
                                className="p-2 hover:bg-slate-700 rounded-lg"
                            >
                                ✕
                            </button>
                        </div>
                        <div className="p-4">
                            <p className="text-slate-400 mb-4">
                                {selectedRuleset.name} • Current: v{selectedRuleset.version}
                            </p>

                            {/* Mock Diff Display */}
                            <div className="bg-slate-900 rounded-lg p-4 font-mono text-sm space-y-2">
                                <div className="text-slate-500">// Changes from v{selectedRuleset.version - 1} → v{selectedRuleset.version}</div>
                                <div className="text-red-400">- credit_score ≥ 680 → ELIGIBLE</div>
                                <div className="text-green-400">+ credit_score ≥ 700 → ELIGIBLE</div>
                                <div className="text-slate-500">  dti ≤ 40% → ELIGIBLE</div>
                                <div className="text-green-400">+ bankruptcy_recent = Yes → NOT_ELIGIBLE (RC007)</div>
                            </div>

                            <p className="text-slate-500 text-sm mt-4">
                                Changed by {selectedRuleset.created_by} on {new Date(selectedRuleset.updated_at).toLocaleString()}
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
