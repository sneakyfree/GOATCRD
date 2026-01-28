import React, { useState, useEffect } from 'react';

interface Ticket {
  id: string;
  case_id: string;
  trigger_reason: string;
  status: string;
  priority: string;
  assigned_to: string | null;
  created_at: string;
  consumer_name: string | null;
  scenario_count: number;
}

interface QueueStats {
  pending: number;
  in_review: number;
  resolved_today: number;
  avg_resolution_hours: number;
}

interface OverrideReason {
  code: string;
  label: string;
  category: 'documentation' | 'exception' | 'correction' | 'escalation';
  requires_evidence: boolean;
  requires_supervisor: boolean;
}

const OVERRIDE_REASONS: OverrideReason[] = [
  { code: 'DOC_VERIFIED', label: 'Additional documentation verified', category: 'documentation', requires_evidence: true, requires_supervisor: false },
  { code: 'INCOME_CORRECTED', label: 'Income calculation corrected', category: 'correction', requires_evidence: true, requires_supervisor: false },
  { code: 'MANUAL_EXCEPTION', label: 'Manual exception approved', category: 'exception', requires_evidence: true, requires_supervisor: true },
  { code: 'RULE_ERROR', label: 'Rule engine error identified', category: 'correction', requires_evidence: true, requires_supervisor: true },
  { code: 'CONSUMER_DISPUTE', label: 'Consumer dispute resolution', category: 'exception', requires_evidence: true, requires_supervisor: false },
  { code: 'POLICY_CHANGE', label: 'Policy change retroactive', category: 'exception', requires_evidence: false, requires_supervisor: true },
  { code: 'SUPERVISOR_OVERRIDE', label: 'Supervisor escalation override', category: 'escalation', requires_evidence: false, requires_supervisor: true },
];

const ReviewQueue: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [stats, setStats] = useState<QueueStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [filter, setFilter] = useState<string>('pending');

  // Override modal state
  const [showOverrideModal, setShowOverrideModal] = useState(false);
  const [selectedReason, setSelectedReason] = useState<OverrideReason | null>(null);
  const [overrideNotes, setOverrideNotes] = useState('');
  const [overrideOutcome, setOverrideOutcome] = useState<'eligible' | 'not_eligible' | 'refer'>('eligible');
  const [supervisorConfirmed, setSupervisorConfirmed] = useState(false);
  const [evidenceUploaded, setEvidenceUploaded] = useState(false);

  useEffect(() => {
    fetchQueue();
    fetchStats();
  }, [filter]);

  const fetchQueue = async () => {
    try {
      const res = await fetch(`/api/v1/review/queue?status_filter=${filter}`);
      if (res.ok) {
        setTickets(await res.json());
      }
    } catch (err) {
      console.error('Failed to fetch queue:', err);
    }
    setLoading(false);
  };

  const fetchStats = async () => {
    try {
      const res = await fetch('/api/v1/review/stats');
      if (res.ok) {
        setStats(await res.json());
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const assignToMe = async (ticketId: string) => {
    try {
      await fetch(`/api/v1/review/tickets/${ticketId}/assign`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewer_id: 'current-user-id' }),
      });
      fetchQueue();
    } catch (err) {
      console.error('Failed to assign:', err);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'priority-urgent';
      case 'high': return 'priority-high';
      case 'normal': return 'priority-normal';
      default: return 'priority-low';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return '⏳';
      case 'in_review': return '🔍';
      case 'resolved': return '✅';
      default: return '❓';
    }
  };

  return (
    <div className="review-queue">
      <header className="queue-header">
        <div>
          <h1>Human Review Queue</h1>
          <p className="subtitle">Cases requiring manual review</p>
        </div>
      </header>

      {/* Stats Cards */}
      {stats && (
        <div className="stats-row">
          <div className="stat-card pending">
            <div className="stat-value">{stats.pending}</div>
            <div className="stat-label">Pending</div>
          </div>
          <div className="stat-card in-review">
            <div className="stat-value">{stats.in_review}</div>
            <div className="stat-label">In Review</div>
          </div>
          <div className="stat-card resolved">
            <div className="stat-value">{stats.resolved_today}</div>
            <div className="stat-label">Resolved Today</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.avg_resolution_hours.toFixed(1)}h</div>
            <div className="stat-label">Avg Resolution</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="filters">
        <button
          className={`filter-btn ${filter === 'pending' ? 'active' : ''}`}
          onClick={() => setFilter('pending')}
        >
          ⏳ Pending
        </button>
        <button
          className={`filter-btn ${filter === 'in_review' ? 'active' : ''}`}
          onClick={() => setFilter('in_review')}
        >
          🔍 In Review
        </button>
        <button
          className={`filter-btn ${filter === 'resolved' ? 'active' : ''}`}
          onClick={() => setFilter('resolved')}
        >
          ✅ Resolved
        </button>
        <button
          className={`filter-btn ${filter === '' ? 'active' : ''}`}
          onClick={() => setFilter('')}
        >
          📋 All
        </button>
      </div>

      {/* Queue List */}
      <div className="queue-container">
        <div className="ticket-list">
          {loading ? (
            <div className="loading">Loading tickets...</div>
          ) : tickets.length === 0 ? (
            <div className="empty-state">
              <span className="empty-icon">🎉</span>
              <p>No tickets in queue!</p>
            </div>
          ) : (
            tickets.map(ticket => (
              <div
                key={ticket.id}
                className={`ticket-card ${selectedTicket?.id === ticket.id ? 'selected' : ''}`}
                onClick={() => setSelectedTicket(ticket)}
              >
                <div className="ticket-header">
                  <span className={`priority-badge ${getPriorityColor(ticket.priority)}`}>
                    {ticket.priority.toUpperCase()}
                  </span>
                  <span className="status-icon">{getStatusIcon(ticket.status)}</span>
                </div>

                <h3 className="ticket-title">
                  Case #{ticket.case_id.slice(0, 8)}
                </h3>

                <p className="ticket-reason">{ticket.trigger_reason}</p>

                <div className="ticket-meta">
                  <span>📊 {ticket.scenario_count} scenarios</span>
                  <span>🕐 {new Date(ticket.created_at).toLocaleDateString()}</span>
                </div>

                {ticket.status === 'pending' && (
                  <button
                    className="assign-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      assignToMe(ticket.id);
                    }}
                  >
                    Assign to Me
                  </button>
                )}
              </div>
            ))
          )}
        </div>

        {/* Detail Panel */}
        {selectedTicket && (
          <div className="detail-panel">
            <div className="detail-header">
              <h2>Ticket Details</h2>
              <button className="close-btn" onClick={() => setSelectedTicket(null)}>✕</button>
            </div>

            <div className="detail-content">
              <div className="detail-row">
                <label>Case ID</label>
                <span>{selectedTicket.case_id}</span>
              </div>
              <div className="detail-row">
                <label>Trigger Reason</label>
                <span>{selectedTicket.trigger_reason}</span>
              </div>
              <div className="detail-row">
                <label>Status</label>
                <span className="status-badge">{selectedTicket.status}</span>
              </div>
              <div className="detail-row">
                <label>Priority</label>
                <span className={`priority-badge ${getPriorityColor(selectedTicket.priority)}`}>
                  {selectedTicket.priority}
                </span>
              </div>
              <div className="detail-row">
                <label>Created</label>
                <span>{new Date(selectedTicket.created_at).toLocaleString()}</span>
              </div>
            </div>

            <div className="detail-actions">
              <button className="btn-primary">View Case</button>
              <button className="btn-secondary">Resolve</button>
              <button
                className="btn-warning"
                onClick={() => setShowOverrideModal(true)}
              >
                Override
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Override Modal */}
      {showOverrideModal && selectedTicket && (
        <div className="modal-overlay" onClick={() => setShowOverrideModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Override Decision</h2>
              <button className="close-btn" onClick={() => setShowOverrideModal(false)}>✕</button>
            </div>

            <div className="modal-body">
              <div className="modal-section">
                <label>Case ID</label>
                <p className="case-id">{selectedTicket.case_id}</p>
              </div>

              <div className="modal-section">
                <label>New Outcome</label>
                <div className="outcome-options">
                  <button
                    className={`outcome-btn eligible ${overrideOutcome === 'eligible' ? 'active' : ''}`}
                    onClick={() => setOverrideOutcome('eligible')}
                  >
                    ✓ Eligible
                  </button>
                  <button
                    className={`outcome-btn refer ${overrideOutcome === 'refer' ? 'active' : ''}`}
                    onClick={() => setOverrideOutcome('refer')}
                  >
                    ⚠ Refer
                  </button>
                  <button
                    className={`outcome-btn not-eligible ${overrideOutcome === 'not_eligible' ? 'active' : ''}`}
                    onClick={() => setOverrideOutcome('not_eligible')}
                  >
                    ✗ Not Eligible
                  </button>
                </div>
              </div>

              <div className="modal-section">
                <label>Override Reason</label>
                <div className="reason-grid">
                  {OVERRIDE_REASONS.map(reason => (
                    <button
                      key={reason.code}
                      className={`reason-btn ${selectedReason?.code === reason.code ? 'active' : ''}`}
                      onClick={() => setSelectedReason(reason)}
                    >
                      <span className={`category-badge ${reason.category}`}>{reason.category}</span>
                      <span className="reason-label">{reason.label}</span>
                      {reason.requires_supervisor && <span className="supervisor-badge">Supervisor</span>}
                    </button>
                  ))}
                </div>
              </div>

              <div className="modal-section">
                <label>Justification Notes</label>
                <textarea
                  value={overrideNotes}
                  onChange={e => setOverrideNotes(e.target.value)}
                  placeholder="Provide detailed justification for this override..."
                  rows={4}
                />
              </div>

              {selectedReason?.requires_evidence && (
                <div className="modal-section requirement">
                  <label>
                    <input
                      type="checkbox"
                      checked={evidenceUploaded}
                      onChange={e => setEvidenceUploaded(e.target.checked)}
                    />
                    Evidence documentation uploaded
                  </label>
                </div>
              )}

              {selectedReason?.requires_supervisor && (
                <div className="modal-section requirement">
                  <label>
                    <input
                      type="checkbox"
                      checked={supervisorConfirmed}
                      onChange={e => setSupervisorConfirmed(e.target.checked)}
                    />
                    Supervisor approval confirmed
                  </label>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowOverrideModal(false)}>
                Cancel
              </button>
              <button
                className="btn-primary"
                disabled={!selectedReason || !overrideNotes ||
                  (selectedReason?.requires_evidence && !evidenceUploaded) ||
                  (selectedReason?.requires_supervisor && !supervisorConfirmed)}
                onClick={() => {
                  console.log('Override submitted:', {
                    case_id: selectedTicket.case_id,
                    reason: selectedReason?.code,
                    outcome: overrideOutcome,
                    notes: overrideNotes
                  });
                  setShowOverrideModal(false);
                  setSelectedReason(null);
                  setOverrideNotes('');
                  setEvidenceUploaded(false);
                  setSupervisorConfirmed(false);
                }}
              >
                Submit Override
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .review-queue {
          max-width: 1400px;
          margin: 0 auto;
          padding: 2rem;
        }
        
        .queue-header h1 {
          font-size: 2rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
        }
        
        .subtitle {
          color: var(--text-secondary, #6b7280);
        }
        
        .stats-row {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 1rem;
          margin: 2rem 0;
        }
        
        .stat-card {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          text-align: center;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .stat-card.pending { border-top: 4px solid #f59e0b; }
        .stat-card.in-review { border-top: 4px solid #6366f1; }
        .stat-card.resolved { border-top: 4px solid #10b981; }
        
        .stat-value {
          font-size: 2.5rem;
          font-weight: 700;
        }
        
        .stat-label {
          color: var(--text-secondary, #6b7280);
          font-size: 0.875rem;
        }
        
        .filters {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1.5rem;
        }
        
        .filter-btn {
          padding: 0.5rem 1rem;
          border: 1px solid var(--border-color, #e5e7eb);
          background: white;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .filter-btn:hover {
          border-color: var(--primary, #6366f1);
        }
        
        .filter-btn.active {
          background: var(--primary, #6366f1);
          color: white;
          border-color: var(--primary, #6366f1);
        }
        
        .queue-container {
          display: grid;
          grid-template-columns: 1fr 400px;
          gap: 1.5rem;
        }
        
        .ticket-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        
        .ticket-card {
          background: white;
          border-radius: 12px;
          padding: 1.25rem;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
          cursor: pointer;
          transition: all 0.2s;
          border: 2px solid transparent;
        }
        
        .ticket-card:hover {
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .ticket-card.selected {
          border-color: var(--primary, #6366f1);
        }
        
        .ticket-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.75rem;
        }
        
        .priority-badge {
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: 600;
        }
        
        .priority-urgent { background: #fef2f2; color: #dc2626; }
        .priority-high { background: #fff7ed; color: #ea580c; }
        .priority-normal { background: #eff6ff; color: #2563eb; }
        .priority-low { background: #f0fdf4; color: #16a34a; }
        
        .ticket-title {
          font-weight: 600;
          margin-bottom: 0.5rem;
        }
        
        .ticket-reason {
          color: var(--text-secondary, #6b7280);
          font-size: 0.875rem;
          margin-bottom: 0.75rem;
        }
        
        .ticket-meta {
          display: flex;
          gap: 1rem;
          font-size: 0.75rem;
          color: var(--text-secondary, #6b7280);
        }
        
        .assign-btn {
          margin-top: 1rem;
          width: 100%;
          padding: 0.5rem;
          background: var(--primary, #6366f1);
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
        }
        
        .detail-panel {
          background: white;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
          position: sticky;
          top: 2rem;
          height: fit-content;
        }
        
        .detail-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem 1.5rem;
          border-bottom: 1px solid var(--border-color, #e5e7eb);
        }
        
        .detail-header h2 {
          font-size: 1.25rem;
          font-weight: 600;
        }
        
        .close-btn {
          background: none;
          border: none;
          font-size: 1.25rem;
          cursor: pointer;
          color: var(--text-secondary, #6b7280);
        }
        
        .detail-content {
          padding: 1.5rem;
        }
        
        .detail-row {
          display: flex;
          justify-content: space-between;
          padding: 0.75rem 0;
          border-bottom: 1px solid var(--border-color, #e5e7eb);
        }
        
        .detail-row label {
          color: var(--text-secondary, #6b7280);
          font-size: 0.875rem;
        }
        
        .detail-actions {
          display: flex;
          gap: 0.5rem;
          padding: 1.5rem;
          border-top: 1px solid var(--border-color, #e5e7eb);
        }
        
        .btn-primary {
          flex: 1;
          padding: 0.75rem;
          background: var(--primary, #6366f1);
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
        }
        
        .btn-secondary {
          flex: 1;
          padding: 0.75rem;
          background: white;
          border: 1px solid var(--border-color, #e5e7eb);
          border-radius: 8px;
          cursor: pointer;
        }
        
        .btn-warning {
          flex: 1;
          padding: 0.75rem;
          background: #fef3c7;
          color: #92400e;
          border: none;
          border-radius: 8px;
          cursor: pointer;
        }
        
        .loading, .empty-state {
          text-align: center;
          padding: 3rem;
          color: var(--text-secondary, #6b7280);
        }
        
        .empty-icon {
          font-size: 3rem;
          display: block;
          margin-bottom: 1rem;
        }

        /* Override Modal Styles */
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.7);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal-content {
          background: white;
          border-radius: 16px;
          width: 90%;
          max-width: 600px;
          max-height: 90vh;
          overflow-y: auto;
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1.5rem;
          border-bottom: 1px solid var(--border-color, #e5e7eb);
        }

        .modal-header h2 {
          font-size: 1.25rem;
          font-weight: 600;
        }

        .modal-body {
          padding: 1.5rem;
        }

        .modal-section {
          margin-bottom: 1.5rem;
        }

        .modal-section label {
          display: block;
          font-weight: 500;
          margin-bottom: 0.5rem;
          color: var(--text-secondary, #6b7280);
        }

        .case-id {
          font-family: monospace;
          font-size: 1rem;
          color: #111;
        }

        .outcome-options {
          display: flex;
          gap: 0.5rem;
        }

        .outcome-btn {
          flex: 1;
          padding: 0.75rem;
          border: 2px solid var(--border-color, #e5e7eb);
          border-radius: 8px;
          background: white;
          cursor: pointer;
          font-weight: 500;
          transition: all 0.2s;
        }

        .outcome-btn.eligible:hover, .outcome-btn.eligible.active {
          background: #d1fae5;
          border-color: #10b981;
          color: #065f46;
        }

        .outcome-btn.refer:hover, .outcome-btn.refer.active {
          background: #fef3c7;
          border-color: #f59e0b;
          color: #92400e;
        }

        .outcome-btn.not-eligible:hover, .outcome-btn.not-eligible.active {
          background: #fee2e2;
          border-color: #ef4444;
          color: #991b1b;
        }

        .reason-grid {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .reason-btn {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem;
          border: 2px solid var(--border-color, #e5e7eb);
          border-radius: 8px;
          background: white;
          cursor: pointer;
          text-align: left;
          transition: all 0.2s;
        }

        .reason-btn:hover, .reason-btn.active {
          border-color: var(--primary, #6366f1);
          background: #f5f3ff;
        }

        .category-badge {
          font-size: 0.7rem;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-weight: 600;
          text-transform: uppercase;
        }

        .category-badge.documentation { background: #dbeafe; color: #1d4ed8; }
        .category-badge.exception { background: #fef3c7; color: #92400e; }
        .category-badge.correction { background: #d1fae5; color: #065f46; }
        .category-badge.escalation { background: #fee2e2; color: #991b1b; }

        .reason-label {
          flex: 1;
          font-weight: 500;
        }

        .supervisor-badge {
          font-size: 0.7rem;
          padding: 0.25rem 0.5rem;
          background: #fef2f2;
          color: #dc2626;
          border-radius: 4px;
          font-weight: 600;
        }

        .modal-section textarea {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid var(--border-color, #e5e7eb);
          border-radius: 8px;
          font-family: inherit;
          resize: vertical;
        }

        .modal-section.requirement label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          cursor: pointer;
        }

        .modal-section.requirement input[type="checkbox"] {
          width: 18px;
          height: 18px;
        }

        .modal-footer {
          display: flex;
          gap: 0.75rem;
          padding: 1.5rem;
          border-top: 1px solid var(--border-color, #e5e7eb);
        }

        .modal-footer .btn-primary:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default ReviewQueue;
