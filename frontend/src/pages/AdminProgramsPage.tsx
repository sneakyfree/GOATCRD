import { useState } from 'react';


// Types
interface Program {
    id: string;
    name: string;
    type: 'credit_card' | 'personal_loan' | 'mortgage' | 'auto_loan';
    provider: string;
    status: 'active' | 'deprecated' | 'draft';
    version: number;
    min_credit_score?: number;
    max_dti?: number;
    geography_constraints: string[];
    pricing_source: 'api' | 'manual' | 'estimate';
    effective_date: string;
    deprecated_date?: string;
    created_at: string;
    updated_at: string;
}

interface ProgramFormData {
    name: string;
    type: Program['type'];
    provider: string;
    min_credit_score: number;
    max_dti: number;
    geography_constraints: string[];
    pricing_source: Program['pricing_source'];
    effective_date: string;
}

// Mock data
const MOCK_PROGRAMS: Program[] = [
    {
        id: '1',
        name: 'Prime Rewards Card',
        type: 'credit_card',
        provider: 'First National Bank',
        status: 'active',
        version: 3,
        min_credit_score: 700,
        max_dti: 0.40,
        geography_constraints: ['ALL'],
        pricing_source: 'api',
        effective_date: '2025-01-01',
        created_at: '2024-06-15T10:00:00Z',
        updated_at: '2025-01-15T14:30:00Z',
    },
    {
        id: '2',
        name: 'FlexLoan Personal',
        type: 'personal_loan',
        provider: 'Credit Union Plus',
        status: 'active',
        version: 2,
        min_credit_score: 650,
        max_dti: 0.45,
        geography_constraints: ['CA', 'NY', 'TX', 'FL'],
        pricing_source: 'manual',
        effective_date: '2024-09-01',
        created_at: '2024-03-20T09:00:00Z',
        updated_at: '2024-11-10T16:45:00Z',
    },
    {
        id: '3',
        name: 'HomePath Mortgage',
        type: 'mortgage',
        provider: 'National Mortgage Corp',
        status: 'deprecated',
        version: 5,
        min_credit_score: 620,
        max_dti: 0.43,
        geography_constraints: ['ALL'],
        pricing_source: 'api',
        effective_date: '2023-01-01',
        deprecated_date: '2025-01-01',
        created_at: '2023-01-01T08:00:00Z',
        updated_at: '2024-12-01T12:00:00Z',
    },
    {
        id: '4',
        name: 'AutoEase Finance',
        type: 'auto_loan',
        provider: 'DriveFinance LLC',
        status: 'draft',
        version: 1,
        min_credit_score: 580,
        max_dti: 0.50,
        geography_constraints: ['CA', 'AZ', 'NV'],
        pricing_source: 'estimate',
        effective_date: '2026-02-01',
        created_at: '2025-12-01T10:00:00Z',
        updated_at: '2026-01-20T11:30:00Z',
    },
];

const PROGRAM_TYPES = [
    { value: 'credit_card', label: 'Credit Card', icon: '💳' },
    { value: 'personal_loan', label: 'Personal Loan', icon: '💰' },
    { value: 'mortgage', label: 'Mortgage', icon: '🏠' },
    { value: 'auto_loan', label: 'Auto Loan', icon: '🚗' },
];

const US_STATES = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
];

export default function AdminProgramsPage() {

    const [programs, setPrograms] = useState<Program[]>(MOCK_PROGRAMS);
    const [filter, setFilter] = useState<'all' | 'active' | 'deprecated' | 'draft'>('all');
    const [typeFilter, setTypeFilter] = useState<string>('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedProgram, setSelectedProgram] = useState<Program | null>(null);
    const [showForm, setShowForm] = useState(false);
    const [showVersionHistory, setShowVersionHistory] = useState(false);
    const [formData, setFormData] = useState<ProgramFormData>({
        name: '',
        type: 'credit_card',
        provider: '',
        min_credit_score: 650,
        max_dti: 0.45,
        geography_constraints: ['ALL'],
        pricing_source: 'manual',
        effective_date: new Date().toISOString().split('T')[0],
    });

    const filteredPrograms = programs.filter(p => {
        if (filter !== 'all' && p.status !== filter) return false;
        if (typeFilter !== 'all' && p.type !== typeFilter) return false;
        if (searchQuery && !p.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
        return true;
    });

    const handleCreate = () => {
        setSelectedProgram(null);
        setFormData({
            name: '',
            type: 'credit_card',
            provider: '',
            min_credit_score: 650,
            max_dti: 0.45,
            geography_constraints: ['ALL'],
            pricing_source: 'manual',
            effective_date: new Date().toISOString().split('T')[0],
        });
        setShowForm(true);
    };

    const handleEdit = (program: Program) => {
        setSelectedProgram(program);
        setFormData({
            name: program.name,
            type: program.type,
            provider: program.provider,
            min_credit_score: program.min_credit_score || 650,
            max_dti: program.max_dti || 0.45,
            geography_constraints: program.geography_constraints,
            pricing_source: program.pricing_source,
            effective_date: program.effective_date,
        });
        setShowForm(true);
    };

    const handleSave = () => {
        if (selectedProgram) {
            // Update existing
            setPrograms(prev => prev.map(p =>
                p.id === selectedProgram.id
                    ? { ...p, ...formData, version: p.version + 1, updated_at: new Date().toISOString() }
                    : p
            ));
        } else {
            // Create new
            const newProgram: Program = {
                id: Date.now().toString(),
                ...formData,
                status: 'draft',
                version: 1,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
            };
            setPrograms(prev => [newProgram, ...prev]);
        }
        setShowForm(false);
    };

    const handleDeprecate = (program: Program) => {
        if (confirm(`Deprecate "${program.name}"? This will trigger a 30-day notice.`)) {
            setPrograms(prev => prev.map(p =>
                p.id === program.id
                    ? {
                        ...p,
                        status: 'deprecated' as const,
                        deprecated_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                        updated_at: new Date().toISOString()
                    }
                    : p
            ));
        }
    };

    const handleActivate = (program: Program) => {
        setPrograms(prev => prev.map(p =>
            p.id === program.id
                ? { ...p, status: 'active' as const, updated_at: new Date().toISOString() }
                : p
        ));
    };

    const getStatusBadge = (status: Program['status']) => {
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

    const getTypeIcon = (type: Program['type']) => {
        return PROGRAM_TYPES.find(t => t.value === type)?.icon || '📄';
    };

    return (
        <div className="min-h-screen bg-slate-900 text-white">
            {/* Header */}
            <div className="bg-slate-800/50 border-b border-slate-700 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-2xl font-bold">Program Catalog</h1>
                            <p className="text-slate-400 text-sm">Manage credit programs, rules, and versions</p>
                        </div>
                        <button
                            onClick={handleCreate}
                            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
                        >
                            <span>+</span> New Program
                        </button>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 py-6">
                {/* Filters */}
                <div className="flex flex-wrap gap-4 mb-6">
                    {/* Search */}
                    <div className="flex-1 min-w-[200px]">
                        <input
                            type="text"
                            placeholder="Search programs..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    {/* Status Filter */}
                    <div className="flex gap-1 bg-slate-800 p-1 rounded-lg">
                        {['all', 'active', 'deprecated', 'draft'].map(status => (
                            <button
                                key={status}
                                onClick={() => setFilter(status as typeof filter)}
                                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${filter === status
                                    ? 'bg-blue-600 text-white'
                                    : 'text-slate-400 hover:text-white'
                                    }`}
                            >
                                {status.charAt(0).toUpperCase() + status.slice(1)}
                            </button>
                        ))}
                    </div>

                    {/* Type Filter */}
                    <select
                        value={typeFilter}
                        onChange={(e) => setTypeFilter(e.target.value)}
                        className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="all">All Types</option>
                        {PROGRAM_TYPES.map(type => (
                            <option key={type.value} value={type.value}>
                                {type.icon} {type.label}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold">{programs.length}</div>
                        <div className="text-slate-400 text-sm">Total Programs</div>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold text-green-400">
                            {programs.filter(p => p.status === 'active').length}
                        </div>
                        <div className="text-slate-400 text-sm">Active</div>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold text-yellow-400">
                            {programs.filter(p => p.status === 'draft').length}
                        </div>
                        <div className="text-slate-400 text-sm">Drafts</div>
                    </div>
                    <div className="bg-slate-800 rounded-lg p-4">
                        <div className="text-2xl font-bold text-red-400">
                            {programs.filter(p => p.status === 'deprecated').length}
                        </div>
                        <div className="text-slate-400 text-sm">Deprecated</div>
                    </div>
                </div>

                {/* Program List */}
                <div className="space-y-3">
                    {filteredPrograms.map(program => (
                        <div
                            key={program.id}
                            className="bg-slate-800 rounded-lg p-4 border border-slate-700 hover:border-slate-600 transition-colors"
                        >
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex items-start gap-4">
                                    <div className="text-3xl">{getTypeIcon(program.type)}</div>
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <h3 className="font-semibold text-lg">{program.name}</h3>
                                            {getStatusBadge(program.status)}
                                            <span className="text-slate-500 text-sm">v{program.version}</span>
                                        </div>
                                        <p className="text-slate-400 text-sm">{program.provider}</p>
                                        <div className="flex flex-wrap gap-4 mt-2 text-sm text-slate-500">
                                            <span>Min Score: {program.min_credit_score || 'N/A'}</span>
                                            <span>Max DTI: {program.max_dti ? `${(program.max_dti * 100).toFixed(0)}%` : 'N/A'}</span>
                                            <span>States: {program.geography_constraints.join(', ')}</span>
                                            <span>Source: {program.pricing_source}</span>
                                        </div>
                                        {program.deprecated_date && (
                                            <p className="text-red-400 text-sm mt-1">
                                                ⚠️ Deprecation: {program.deprecated_date}
                                            </p>
                                        )}
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => handleEdit(program)}
                                        className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
                                        title="Edit"
                                    >
                                        ✏️
                                    </button>
                                    <button
                                        onClick={() => { setSelectedProgram(program); setShowVersionHistory(true); }}
                                        className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
                                        title="Version History"
                                    >
                                        📜
                                    </button>
                                    {program.status === 'active' && (
                                        <button
                                            onClick={() => handleDeprecate(program)}
                                            className="p-2 bg-red-600/20 hover:bg-red-600/40 text-red-400 rounded-lg transition-colors"
                                            title="Deprecate"
                                        >
                                            🗑️
                                        </button>
                                    )}
                                    {program.status === 'draft' && (
                                        <button
                                            onClick={() => handleActivate(program)}
                                            className="p-2 bg-green-600/20 hover:bg-green-600/40 text-green-400 rounded-lg transition-colors"
                                            title="Activate"
                                        >
                                            ✅
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {filteredPrograms.length === 0 && (
                    <div className="text-center py-12 text-slate-500">
                        <div className="text-4xl mb-4">📋</div>
                        <p>No programs found matching your filters.</p>
                    </div>
                )}
            </div>

            {/* Create/Edit Modal */}
            {showForm && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-slate-800 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                        <div className="sticky top-0 bg-slate-800 p-4 border-b border-slate-700 flex items-center justify-between">
                            <h2 className="text-xl font-semibold">
                                {selectedProgram ? 'Edit Program' : 'Create New Program'}
                            </h2>
                            <button
                                onClick={() => setShowForm(false)}
                                className="p-2 hover:bg-slate-700 rounded-lg"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="p-4 space-y-4">
                            {/* Name */}
                            <div>
                                <label className="block text-sm font-medium mb-1">Program Name</label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2"
                                    placeholder="e.g., Prime Rewards Card"
                                />
                            </div>

                            {/* Type */}
                            <div>
                                <label className="block text-sm font-medium mb-1">Type</label>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                                    {PROGRAM_TYPES.map(type => (
                                        <button
                                            key={type.value}
                                            onClick={() => setFormData(prev => ({ ...prev, type: type.value as Program['type'] }))}
                                            className={`p-3 rounded-lg border text-center transition-colors ${formData.type === type.value
                                                ? 'bg-blue-600 border-blue-500'
                                                : 'bg-slate-900 border-slate-700 hover:border-slate-600'
                                                }`}
                                        >
                                            <div className="text-2xl mb-1">{type.icon}</div>
                                            <div className="text-sm">{type.label}</div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Provider */}
                            <div>
                                <label className="block text-sm font-medium mb-1">Provider</label>
                                <input
                                    type="text"
                                    value={formData.provider}
                                    onChange={(e) => setFormData(prev => ({ ...prev, provider: e.target.value }))}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2"
                                    placeholder="e.g., First National Bank"
                                />
                            </div>

                            {/* Eligibility Rules */}
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Min Credit Score</label>
                                    <input
                                        type="number"
                                        value={formData.min_credit_score}
                                        onChange={(e) => setFormData(prev => ({ ...prev, min_credit_score: parseInt(e.target.value) }))}
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2"
                                        min={300}
                                        max={850}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Max DTI (%)</label>
                                    <input
                                        type="number"
                                        value={(formData.max_dti * 100).toFixed(0)}
                                        onChange={(e) => setFormData(prev => ({ ...prev, max_dti: parseInt(e.target.value) / 100 }))}
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2"
                                        min={0}
                                        max={100}
                                    />
                                </div>
                            </div>

                            {/* Pricing Source */}
                            <div>
                                <label className="block text-sm font-medium mb-1">Pricing Source</label>
                                <select
                                    value={formData.pricing_source}
                                    onChange={(e) => setFormData(prev => ({ ...prev, pricing_source: e.target.value as Program['pricing_source'] }))}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2"
                                >
                                    <option value="api">API (Real-time)</option>
                                    <option value="manual">Manual Entry</option>
                                    <option value="estimate">Estimate</option>
                                </select>
                            </div>

                            {/* Effective Date */}
                            <div>
                                <label className="block text-sm font-medium mb-1">Effective Date</label>
                                <input
                                    type="date"
                                    value={formData.effective_date}
                                    onChange={(e) => setFormData(prev => ({ ...prev, effective_date: e.target.value }))}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2"
                                />
                            </div>

                            {/* Geography */}
                            <div>
                                <label className="block text-sm font-medium mb-1">Geography Constraints</label>
                                <div className="flex flex-wrap gap-1 p-2 bg-slate-900 border border-slate-700 rounded-lg max-h-32 overflow-y-auto">
                                    <button
                                        onClick={() => setFormData(prev => ({ ...prev, geography_constraints: ['ALL'] }))}
                                        className={`px-2 py-1 text-xs rounded ${formData.geography_constraints.includes('ALL')
                                            ? 'bg-blue-600'
                                            : 'bg-slate-700 hover:bg-slate-600'
                                            }`}
                                    >
                                        All States
                                    </button>
                                    {US_STATES.map(state => (
                                        <button
                                            key={state}
                                            onClick={() => {
                                                setFormData(prev => {
                                                    const constraints = prev.geography_constraints.filter(s => s !== 'ALL');
                                                    return {
                                                        ...prev,
                                                        geography_constraints: constraints.includes(state)
                                                            ? constraints.filter(s => s !== state)
                                                            : [...constraints, state]
                                                    };
                                                });
                                            }}
                                            className={`px-2 py-1 text-xs rounded ${formData.geography_constraints.includes(state) || formData.geography_constraints.includes('ALL')
                                                ? 'bg-blue-600'
                                                : 'bg-slate-700 hover:bg-slate-600'
                                                }`}
                                        >
                                            {state}
                                        </button>
                                    ))}
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
                                {selectedProgram ? 'Save Changes' : 'Create Program'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Version History Modal */}
            {showVersionHistory && selectedProgram && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-slate-800 rounded-xl w-full max-w-lg">
                        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
                            <h2 className="text-xl font-semibold">Version History</h2>
                            <button
                                onClick={() => setShowVersionHistory(false)}
                                className="p-2 hover:bg-slate-700 rounded-lg"
                            >
                                ✕
                            </button>
                        </div>
                        <div className="p-4 space-y-3">
                            <div className="text-slate-400 text-sm mb-4">
                                {selectedProgram.name} • Current: v{selectedProgram.version}
                            </div>
                            {Array.from({ length: selectedProgram.version }, (_, i) => selectedProgram.version - i).map(v => (
                                <div
                                    key={v}
                                    className={`p-3 rounded-lg border ${v === selectedProgram.version
                                        ? 'bg-blue-600/20 border-blue-500/50'
                                        : 'bg-slate-900 border-slate-700'
                                        }`}
                                >
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <span className="font-medium">Version {v}</span>
                                            {v === selectedProgram.version && (
                                                <span className="ml-2 text-xs text-blue-400">(Current)</span>
                                            )}
                                        </div>
                                        <span className="text-slate-500 text-sm">
                                            {new Date(selectedProgram.updated_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                    {v < selectedProgram.version && (
                                        <button className="text-blue-400 text-sm mt-1 hover:underline">
                                            View diff from v{v} → v{selectedProgram.version}
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
