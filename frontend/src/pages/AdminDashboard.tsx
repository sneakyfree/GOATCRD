import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface Program {
    id: string;
    program_code: string;
    name: string;
    program_type: string;
    is_active: boolean;
    version: number;
}

interface Ruleset {
    id: string;
    name: string;
    description: string | null;
    is_active: boolean;
    version: number;
}

interface FairnessMetrics {
    total_tests: number;
    passed: number;
    failed: number;
    warnings: number;
    current_deployment_status: string;
    avg_air_score: number;
}

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            className="tab-panel"
        >
            {value === index && <div className="tab-content">{children}</div>}
        </div>
    );
};

const AdminDashboard: React.FC = () => {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState(0);
    const [programs, setPrograms] = useState<Program[]>([]);
    const [rulesets, setRulesets] = useState<Ruleset[]>([]);
    const [fairnessMetrics, setFairnessMetrics] = useState<FairnessMetrics | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch data on mount
    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);

                // Fetch programs
                const programsRes = await fetch('/api/v1/admin/programs');
                if (programsRes.ok) {
                    setPrograms(await programsRes.json());
                }

                // Fetch rulesets
                const rulesetsRes = await fetch('/api/v1/admin/rulesets');
                if (rulesetsRes.ok) {
                    setRulesets(await rulesetsRes.json());
                }

                // Fetch fairness metrics
                const fairnessRes = await fetch('/api/v1/admin/fairness/dashboard');
                if (fairnessRes.ok) {
                    setFairnessMetrics(await fairnessRes.json());
                }

                setLoading(false);
            } catch (err) {
                setError('Failed to load admin data');
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const tabs = ['Programs', 'Rulesets', 'Fairness', 'Users'];

    return (
        <div className="admin-dashboard">
            <header className="admin-header">
                <h1>Admin Dashboard</h1>
                <p className="subtitle">Manage programs, rules, and compliance</p>
            </header>

            {/* Tab Navigation */}
            <nav className="admin-tabs">
                {tabs.map((tab, index) => (
                    <button
                        key={tab}
                        className={`tab-button ${activeTab === index ? 'active' : ''}`}
                        onClick={() => setActiveTab(index)}
                    >
                        {tab}
                    </button>
                ))}
            </nav>

            {loading && (
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Loading admin data...</p>
                </div>
            )}

            {error && (
                <div className="error-banner">
                    <span className="error-icon">⚠️</span>
                    {error}
                </div>
            )}

            {!loading && !error && (
                <>
                    {/* Programs Tab */}
                    <TabPanel value={activeTab} index={0}>
                        <div className="panel-header">
                            <h2>Program Catalog</h2>
                            <button className="btn-primary" onClick={() => navigate('/admin/programs/new')}>
                                + Add Program
                            </button>
                        </div>

                        <div className="data-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Code</th>
                                        <th>Name</th>
                                        <th>Type</th>
                                        <th>Status</th>
                                        <th>Version</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {programs.map(program => (
                                        <tr key={program.id}>
                                            <td><code>{program.program_code}</code></td>
                                            <td>{program.name}</td>
                                            <td className="capitalize">{program.program_type.replace('_', ' ')}</td>
                                            <td>
                                                <span className={`status-badge ${program.is_active ? 'active' : 'inactive'}`}>
                                                    {program.is_active ? 'Active' : 'Deprecated'}
                                                </span>
                                            </td>
                                            <td>v{program.version}</td>
                                            <td>
                                                <button className="btn-icon" title="Edit">✏️</button>
                                                <button className="btn-icon" title="History">📜</button>
                                            </td>
                                        </tr>
                                    ))}
                                    {programs.length === 0 && (
                                        <tr>
                                            <td colSpan={6} className="empty-state">No programs found</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </TabPanel>

                    {/* Rulesets Tab */}
                    <TabPanel value={activeTab} index={1}>
                        <div className="panel-header">
                            <h2>Eligibility Rulesets</h2>
                            <button className="btn-primary" onClick={() => navigate('/admin/rulesets/new')}>
                                + Add Ruleset
                            </button>
                        </div>

                        <div className="data-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Description</th>
                                        <th>Status</th>
                                        <th>Version</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {rulesets.map(ruleset => (
                                        <tr key={ruleset.id}>
                                            <td><strong>{ruleset.name}</strong></td>
                                            <td>{ruleset.description || '—'}</td>
                                            <td>
                                                <span className={`status-badge ${ruleset.is_active ? 'active' : 'inactive'}`}>
                                                    {ruleset.is_active ? 'Active' : 'Inactive'}
                                                </span>
                                            </td>
                                            <td>v{ruleset.version}</td>
                                            <td>
                                                <button className="btn-icon" title="Edit">✏️</button>
                                                <button className="btn-icon" title="Test">🧪</button>
                                            </td>
                                        </tr>
                                    ))}
                                    {rulesets.length === 0 && (
                                        <tr>
                                            <td colSpan={5} className="empty-state">No rulesets found</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </TabPanel>

                    {/* Fairness Tab */}
                    <TabPanel value={activeTab} index={2}>
                        <div className="panel-header">
                            <h2>Fairness Monitoring</h2>
                            <button className="btn-primary" onClick={() => navigate('/admin/fairness/run')}>
                                Run Tests
                            </button>
                        </div>

                        {fairnessMetrics && (
                            <div className="metrics-grid">
                                <div className="metric-card">
                                    <div className="metric-value">{fairnessMetrics.total_tests}</div>
                                    <div className="metric-label">Total Tests</div>
                                </div>
                                <div className="metric-card passed">
                                    <div className="metric-value">{fairnessMetrics.passed}</div>
                                    <div className="metric-label">Passed</div>
                                </div>
                                <div className="metric-card failed">
                                    <div className="metric-value">{fairnessMetrics.failed}</div>
                                    <div className="metric-label">Failed</div>
                                </div>
                                <div className="metric-card warning">
                                    <div className="metric-value">{fairnessMetrics.warnings}</div>
                                    <div className="metric-label">Warnings</div>
                                </div>
                                <div className="metric-card">
                                    <div className="metric-value">{(fairnessMetrics.avg_air_score * 100).toFixed(0)}%</div>
                                    <div className="metric-label">Avg AIR Score</div>
                                </div>
                                <div className={`metric-card deployment ${fairnessMetrics.current_deployment_status}`}>
                                    <div className="metric-value capitalize">{fairnessMetrics.current_deployment_status}</div>
                                    <div className="metric-label">Deployment Status</div>
                                </div>
                            </div>
                        )}

                        <div className="section-divider"></div>

                        <h3>Recent Test History</h3>
                        <button className="btn-secondary" onClick={() => navigate('/admin/fairness/history')}>
                            View All History →
                        </button>
                    </TabPanel>

                    {/* Users Tab */}
                    <TabPanel value={activeTab} index={3}>
                        <div className="panel-header">
                            <h2>User Management</h2>
                            <button className="btn-primary">+ Add User</button>
                        </div>
                        <p className="coming-soon">User management coming soon...</p>
                    </TabPanel>
                </>
            )}

            <style>{`
        .admin-dashboard {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
        }
        
        .admin-header {
          margin-bottom: 2rem;
        }
        
        .admin-header h1 {
          font-size: 2rem;
          font-weight: 700;
          color: var(--text-primary, #1a1a2e);
          margin-bottom: 0.5rem;
        }
        
        .subtitle {
          color: var(--text-secondary, #6b7280);
        }
        
        .admin-tabs {
          display: flex;
          gap: 0.5rem;
          border-bottom: 2px solid var(--border-color, #e5e7eb);
          margin-bottom: 2rem;
        }
        
        .tab-button {
          padding: 0.75rem 1.5rem;
          background: none;
          border: none;
          font-size: 1rem;
          font-weight: 500;
          color: var(--text-secondary, #6b7280);
          cursor: pointer;
          border-bottom: 2px solid transparent;
          margin-bottom: -2px;
          transition: all 0.2s;
        }
        
        .tab-button:hover {
          color: var(--primary, #6366f1);
        }
        
        .tab-button.active {
          color: var(--primary, #6366f1);
          border-bottom-color: var(--primary, #6366f1);
        }
        
        .panel-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        
        .panel-header h2 {
          font-size: 1.5rem;
          font-weight: 600;
        }
        
        .btn-primary {
          background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
          transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn-primary:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }
        
        .btn-secondary {
          background: white;
          color: var(--primary, #6366f1);
          border: 1px solid var(--primary, #6366f1);
          padding: 0.5rem 1rem;
          border-radius: 6px;
          cursor: pointer;
        }
        
        .btn-icon {
          background: none;
          border: none;
          cursor: pointer;
          font-size: 1rem;
          padding: 0.25rem;
          opacity: 0.7;
          transition: opacity 0.2s;
        }
        
        .btn-icon:hover {
          opacity: 1;
        }
        
        .data-table {
          background: white;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          overflow: hidden;
        }
        
        .data-table table {
          width: 100%;
          border-collapse: collapse;
        }
        
        .data-table th,
        .data-table td {
          padding: 1rem;
          text-align: left;
          border-bottom: 1px solid var(--border-color, #e5e7eb);
        }
        
        .data-table th {
          background: var(--bg-secondary, #f9fafb);
          font-weight: 600;
          font-size: 0.875rem;
          color: var(--text-secondary, #6b7280);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        
        .status-badge {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 500;
        }
        
        .status-badge.active {
          background: #d1fae5;
          color: #065f46;
        }
        
        .status-badge.inactive {
          background: #fef3c7;
          color: #92400e;
        }
        
        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 1rem;
          margin-bottom: 2rem;
        }
        
        .metric-card {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          text-align: center;
        }
        
        .metric-card.passed { border-left: 4px solid #10b981; }
        .metric-card.failed { border-left: 4px solid #ef4444; }
        .metric-card.warning { border-left: 4px solid #f59e0b; }
        .metric-card.deployment.allowed { border-left: 4px solid #10b981; }
        .metric-card.deployment.blocked { border-left: 4px solid #ef4444; }
        .metric-card.deployment.pending_approval { border-left: 4px solid #f59e0b; }
        
        .metric-value {
          font-size: 2rem;
          font-weight: 700;
          color: var(--text-primary, #1a1a2e);
        }
        
        .metric-label {
          font-size: 0.875rem;
          color: var(--text-secondary, #6b7280);
          margin-top: 0.25rem;
        }
        
        .capitalize {
          text-transform: capitalize;
        }
        
        .loading-state {
          text-align: center;
          padding: 4rem;
        }
        
        .spinner {
          width: 40px;
          height: 40px;
          border: 3px solid var(--border-color, #e5e7eb);
          border-top-color: var(--primary, #6366f1);
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 1rem;
        }
        
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        
        .error-banner {
          background: #fef2f2;
          color: #991b1b;
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 1rem;
        }
        
        .empty-state {
          text-align: center;
          color: var(--text-secondary, #6b7280);
          padding: 2rem !important;
        }
        
        .section-divider {
          height: 1px;
          background: var(--border-color, #e5e7eb);
          margin: 2rem 0;
        }
        
        .coming-soon {
          color: var(--text-secondary, #6b7280);
          font-style: italic;
        }
      `}</style>
        </div>
    );
};

export default AdminDashboard;
