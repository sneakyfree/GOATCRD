import { useState } from 'react';

// Types
interface ReasonCode {
    id: string;
    code: string;
    category: string;
    description: string;
    consumer_message: string;
    improvement_hint: string;
    severity: 'blockers' | 'major' | 'minor';
    rule_triggers: string[];
    created_at: string;
    updated_at: string;
}

// Mock data - aligned with DNA Strand Master Plan Section 11
const MOCK_REASON_CODES: ReasonCode[] = [
    {
        id: '1',
        code: 'RC001',
        category: 'Credit History',
        description: 'Insufficient credit history',
        consumer_message: 'Your credit history is limited, which affects lender confidence.',
        improvement_hint: 'Building more credit history through responsible use may improve your eligibility.',
        severity: 'major',
        rule_triggers: ['thin_file = true', 'credit_age_months < 24'],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2025-01-15T10:00:00Z',
    },
    {
        id: '2',
        code: 'RC002',
        category: 'Credit Score',
        description: 'Credit score below threshold',
        consumer_message: 'Your credit score does not meet the minimum requirement for this product.',
        improvement_hint: 'Improving your credit score through on-time payments may help.',
        severity: 'blockers',
        rule_triggers: ['credit_score < program.min_score'],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2025-01-15T10:00:00Z',
    },
    {
        id: '3',
        code: 'RC003',
        category: 'Debt-to-Income',
        description: 'Debt-to-income ratio too high',
        consumer_message: 'Your debt payments relative to income exceed the acceptable limit.',
        improvement_hint: 'Reducing existing debt or increasing income may improve eligibility.',
        severity: 'blockers',
        rule_triggers: ['dti > program.max_dti'],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2025-01-15T10:00:00Z',
    },
    {
        id: '4',
        code: 'RC004',
        category: 'Income',
        description: 'Insufficient income',
        consumer_message: 'Your stated income does not meet the minimum requirement.',
        improvement_hint: 'Documenting additional income sources may help.',
        severity: 'major',
        rule_triggers: ['income < program.min_income'],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2025-01-15T10:00:00Z',
    },
    {
        id: '5',
        code: 'RC005',
        category: 'Verification',
        description: 'Unverifiable income',
        consumer_message: 'We were unable to verify your income from the sources provided.',
        improvement_hint: 'Providing additional documentation may resolve this.',
        severity: 'minor',
        rule_triggers: ['income_source = unknown', 'income_verified = false'],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2025-01-15T10:00:00Z',
    },
    {
        id: '6',
        code: 'RC006',
        category: 'Payment History',
        description: 'Recent delinquency',
        consumer_message: 'Your credit report shows recent late payments.',
        improvement_hint: 'Maintaining on-time payments for 12-24 months may improve eligibility.',
        severity: 'major',
        rule_triggers: ['delinquency_months < 24'],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2025-01-15T10:00:00Z',
    },
    {
        id: '7',
        code: 'RC007',
        category: 'Public Records',
        description: 'Recent bankruptcy',
        consumer_message: 'Your credit report shows a recent bankruptcy filing.',
        improvement_hint: 'Time since bankruptcy is an important factor; eligibility may improve over time.',
        severity: 'blockers',
        rule_triggers: ['bankruptcy_months < 48'],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2025-01-15T10:00:00Z',
    },
    {
        id: '8',
        code: 'RC008',
        category: 'Geography',
        description: 'State/geography ineligible',
        consumer_message: 'This product is not available in your state.',
        improvement_hint: 'Consider alternative products that are available in your area.',
        severity: 'blockers',
        rule_triggers: ['state not in program.states'],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2025-01-15T10:00:00Z',
    },
    {
        id: '9',
        code: 'RC009',
        category: 'Verification',
        description: 'Missing required verification',
        consumer_message: 'Additional documentation is required to complete your application.',
        improvement_hint: 'Please provide the requested documents to proceed.',
        severity: 'minor',
        rule_triggers: ['verified_fields < required'],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2025-01-15T10:00:00Z',
    },
];

const CATEGORIES = [
    'Credit History',
    'Credit Score',
    'Debt-to-Income',
    'Income',
    'Verification',
    'Payment History',
    'Public Records',
    'Geography',
    'Assets',
    'Employment',
];

const SEVERITIES = [
    { value: 'blockers', label: 'Blocker', color: 'text-red-400 bg-red-500/20', icon: '🚫' },
    { value: 'major', label: 'Major', color: 'text-orange-400 bg-orange-500/20', icon: '⚠️' },
    { value: 'minor', label: 'Minor', color: 'text-yellow-400 bg-yellow-500/20', icon: '📝' },
];

export default function AdminReasonCodesPage() {
    const [reasonCodes, setReasonCodes] = useState<ReasonCode[]>(MOCK_REASON_CODES);
    const [selectedCode, setSelectedCode] = useState<ReasonCode | null>(null);
    const [showForm, setShowForm] = useState(false);
    const [categoryFilter, setCategoryFilter] = useState<string>('all');
    const [severityFilter, setSeverityFilter] = useState<string>('all');
    const [searchQuery, setSearchQuery] = useState('');

    const filteredCodes = reasonCodes.filter(rc => {
        if (categoryFilter !== 'all' && rc.category !== categoryFilter) return false;
        if (severityFilter !== 'all' && rc.severity !== severityFilter) return false;
        if (searchQuery) {
            const q = searchQuery.toLowerCase();
            return rc.code.toLowerCase().includes(q) ||
                rc.description.toLowerCase().includes(q) ||
                rc.consumer_message.toLowerCase().includes(q);
        }
        return true;
    });

    const handleEdit = (code: ReasonCode) => {
        setSelectedCode(code);
        setShowForm(true);
    };

    const handleCreate = () => {
        const newCode: ReasonCode = {
            id: Date.now().toString(),
            code: `RC${(reasonCodes.length + 1).toString().padStart(3, '0')}`,
            category: 'Credit Score',
            description: '',
            consumer_message: '',
            improvement_hint: '',
            severity: 'major',
            rule_triggers: [],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
        };
        setSelectedCode(newCode);
        setShowForm(true);
    };

    const handleSave = () => {
        if (!selectedCode) return;

        if (reasonCodes.find(rc => rc.id === selectedCode.id)) {
            setReasonCodes(prev => prev.map(rc =>
                rc.id === selectedCode.id
                    ? { ...selectedCode, updated_at: new Date().toISOString() }
                    : rc
            ));
        } else {
            setReasonCodes(prev => [...prev, selectedCode]);
        }
        setShowForm(false);
    };

    const getSeverityBadge = (severity: ReasonCode['severity']) => {
        const s = SEVERITIES.find(x => x.value === severity);
        return (
            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${s?.color}`}>
                {s?.icon} {s?.label}
            </span>
        );
    };


    return (
        <div className="min-h-screen bg-slate-900 text-white">
            {/* Header */}
            <div className="bg-slate-800/50 border-b border-slate-700 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-2xl font-bold">Reason Code Mapping</h1>
                            <p className="text-slate-400 text-sm">Adverse-action-safe codes per DNA Strand Law 4</p>
                        </div>
                        <button
                            onClick={handleCreate}
                            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
                        >
                            <span>+</span> New Code
                        </button>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 py-6">
                {/* Filters */}
                <div className="flex flex-wrap gap-4 mb-6">
                    <div className="flex-1 min-w-[200px]">
                        <input
                            type="text"
                            placeholder="Search codes..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2"
                        />
                    </div>
                    <select
                        value={categoryFilter}
                        onChange={(e) => setCategoryFilter(e.target.value)}
                        className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2"
                    >
                        <option value="all">All Categories</option>
                        {CATEGORIES.map(cat => (
                            <option key={cat} value={cat}>{cat}</option>
                        ))}
                    </select>
                    <select
                        value={severityFilter}
                        onChange={(e) => setSeverityFilter(e.target.value)}
                        className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2"
                    >
                        <option value="all">All Severities</option>
                        {SEVERITIES.map(s => (
                            <option key={s.value} value={s.value}>{s.icon} {s.label}</option>
                        ))}
                    </select>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold">{reasonCodes.length}</div>
                        <div className="text-slate-400 text-sm">Total Codes</div>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold text-red-400">
                            {reasonCodes.filter(rc => rc.severity === 'blockers').length}
                        </div>
                        <div className="text-slate-400 text-sm">Blockers</div>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold text-orange-400">
                            {reasonCodes.filter(rc => rc.severity === 'major').length}
                        </div>
                        <div className="text-slate-400 text-sm">Major</div>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold text-yellow-400">
                            {reasonCodes.filter(rc => rc.severity === 'minor').length}
                        </div>
                        <div className="text-slate-400 text-sm">Minor</div>
                    </div>
                </div>

                {/* Reason Codes Grid */}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {filteredCodes.map(code => (
                        <div
                            key={code.id}
                            onClick={() => handleEdit(code)}
                            className="bg-slate-800 rounded-lg p-4 border border-slate-700 hover:border-blue-500 cursor-pointer transition-colors"
                        >
                            <div className="flex items-center justify-between mb-2">
                                <span className="font-mono font-bold text-blue-400">{code.code}</span>
                                {getSeverityBadge(code.severity)}
                            </div>
                            <h3 className="font-medium mb-1">{code.description}</h3>
                            <p className="text-slate-400 text-sm mb-3">{code.consumer_message}</p>

                            <div className="text-xs text-slate-500 mb-2">
                                Category: <span className="text-slate-400">{code.category}</span>
                            </div>

                            <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-2 text-sm">
                                <div className="text-green-400 text-xs font-medium mb-1">💡 Improvement Hint</div>
                                <p className="text-slate-300">{code.improvement_hint}</p>
                            </div>

                            <div className="mt-3 flex flex-wrap gap-1">
                                {code.rule_triggers.map((trigger, i) => (
                                    <span key={i} className="text-xs bg-slate-700 px-2 py-1 rounded font-mono">
                                        {trigger}
                                    </span>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                {filteredCodes.length === 0 && (
                    <div className="text-center py-12 text-slate-500">
                        <div className="text-4xl mb-4">📋</div>
                        <p>No reason codes found matching your filters.</p>
                    </div>
                )}
            </div>

            {/* Edit Form Modal */}
            {showForm && selectedCode && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-slate-800 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                        <div className="sticky top-0 bg-slate-800 p-4 border-b border-slate-700 flex items-center justify-between">
                            <h2 className="text-xl font-semibold">
                                {reasonCodes.find(rc => rc.id === selectedCode.id) ? 'Edit' : 'Create'} Reason Code
                            </h2>
                            <button
                                onClick={() => setShowForm(false)}
                                className="p-2 hover:bg-slate-700 rounded-lg"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="p-4 space-y-4">
                            {/* Code & Category */}
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Code</label>
                                    <input
                                        type="text"
                                        value={selectedCode.code}
                                        onChange={(e) => setSelectedCode({ ...selectedCode, code: e.target.value })}
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 font-mono"
                                        placeholder="RC001"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Category</label>
                                    <select
                                        value={selectedCode.category}
                                        onChange={(e) => setSelectedCode({ ...selectedCode, category: e.target.value })}
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2"
                                    >
                                        {CATEGORIES.map(cat => (
                                            <option key={cat} value={cat}>{cat}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            {/* Severity */}
                            <div>
                                <label className="block text-sm font-medium mb-1">Severity</label>
                                <div className="flex gap-2">
                                    {SEVERITIES.map(s => (
                                        <button
                                            key={s.value}
                                            onClick={() => setSelectedCode({ ...selectedCode, severity: s.value as ReasonCode['severity'] })}
                                            className={`px-4 py-2 rounded-lg border transition-colors ${selectedCode.severity === s.value
                                                ? `${s.color} border-current`
                                                : 'bg-slate-900 border-slate-700 hover:border-slate-600'
                                                }`}
                                        >
                                            {s.icon} {s.label}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Description */}
                            <div>
                                <label className="block text-sm font-medium mb-1">Internal Description</label>
                                <input
                                    type="text"
                                    value={selectedCode.description}
                                    onChange={(e) => setSelectedCode({ ...selectedCode, description: e.target.value })}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2"
                                    placeholder="Brief internal description"
                                />
                            </div>

                            {/* Consumer Message */}
                            <div>
                                <label className="block text-sm font-medium mb-1">Consumer-Facing Message</label>
                                <textarea
                                    value={selectedCode.consumer_message}
                                    onChange={(e) => setSelectedCode({ ...selectedCode, consumer_message: e.target.value })}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 h-20"
                                    placeholder="Clear, compliant message for the consumer"
                                />
                            </div>

                            {/* Improvement Hint */}
                            <div>
                                <label className="block text-sm font-medium mb-1">
                                    Improvement Hint
                                    <span className="text-slate-500 font-normal ml-2">(directional, no promises)</span>
                                </label>
                                <textarea
                                    value={selectedCode.improvement_hint}
                                    onChange={(e) => setSelectedCode({ ...selectedCode, improvement_hint: e.target.value })}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 h-20"
                                    placeholder="What actions may improve eligibility"
                                />
                            </div>

                            {/* Rule Triggers */}
                            <div>
                                <label className="block text-sm font-medium mb-1">Rule Triggers</label>
                                <div className="bg-slate-900 border border-slate-700 rounded-lg p-3">
                                    <div className="flex flex-wrap gap-2 mb-2">
                                        {selectedCode.rule_triggers.map((trigger, i) => (
                                            <span key={i} className="flex items-center gap-1 bg-slate-700 px-2 py-1 rounded font-mono text-sm">
                                                {trigger}
                                                <button
                                                    onClick={() => setSelectedCode({
                                                        ...selectedCode,
                                                        rule_triggers: selectedCode.rule_triggers.filter((_, j) => j !== i)
                                                    })}
                                                    className="text-red-400 hover:text-red-300 ml-1"
                                                >
                                                    ×
                                                </button>
                                            </span>
                                        ))}
                                    </div>
                                    <input
                                        type="text"
                                        placeholder="Add trigger (e.g., credit_score < 650) and press Enter"
                                        className="w-full bg-transparent border-none outline-none text-sm"
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter' && e.currentTarget.value) {
                                                setSelectedCode({
                                                    ...selectedCode,
                                                    rule_triggers: [...selectedCode.rule_triggers, e.currentTarget.value]
                                                });
                                                e.currentTarget.value = '';
                                            }
                                        }}
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="sticky bottom-0 bg-slate-800 p-4 border-t border-slate-700 flex justify-end gap-3">
                            <button
                                onClick={() => setShowForm(false)}
                                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSave}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium"
                            >
                                Save Reason Code
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
