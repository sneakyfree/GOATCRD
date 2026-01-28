import React, { useState, useEffect } from 'react';

interface AgentStatus {
  role: string;
  status: 'idle' | 'running' | 'waiting' | 'completed' | 'failed';
  current_task: string | null;
  last_decision: string | null;
  confidence: number | null;
}

interface AgentDecision {
  id: string;
  agent_role: string;
  decision_type: string;
  recommendation: string;
  confidence: number;
  reasoning: string;
  requires_human_review: boolean;
  created_at: string;
}

interface TaskExecution {
  id: string;
  agent_role: string;
  action: string;
  started_at: string;
  completed_at: string | null;
  status: string;
  duration_ms: number | null;
}

const AgentMonitor: React.FC = () => {
  const [agents, setAgents] = useState<AgentStatus[]>([
    { role: 'Intake Specialist', status: 'idle', current_task: null, last_decision: null, confidence: null },
    { role: 'Scenario Analyst', status: 'idle', current_task: null, last_decision: null, confidence: null },
    { role: 'Compliance Reviewer', status: 'idle', current_task: null, last_decision: null, confidence: null },
    { role: 'Coach', status: 'idle', current_task: null, last_decision: null, confidence: null },
  ]);

  const [recentDecisions, _setRecentDecisions] = useState<AgentDecision[]>([]);
  const [taskTimeline, _setTaskTimeline] = useState<TaskExecution[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  // Silences lint warnings - these setters will be used when API integration is added
  void _setRecentDecisions;
  void _setTaskTimeline;

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate agent activity
      setAgents(prev => prev.map(agent => ({
        ...agent,
        status: Math.random() > 0.7 ? 'running' : 'idle',
      })));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'status-running';
      case 'waiting': return 'status-waiting';
      case 'completed': return 'status-completed';
      case 'failed': return 'status-failed';
      default: return 'status-idle';
    }
  };

  const getAgentIcon = (role: string) => {
    if (role.includes('Intake')) return '📝';
    if (role.includes('Scenario')) return '📊';
    if (role.includes('Compliance')) return '⚖️';
    if (role.includes('Coach')) return '🎯';
    return '🤖';
  };

  return (
    <div className="agent-monitor">
      <header className="monitor-header">
        <h1>Agent Monitor</h1>
        <p className="subtitle">Real-time visibility into AI agent activity</p>
        <div className="live-indicator">
          <span className="pulse"></span>
          Live
        </div>
      </header>

      {/* Agent Status Grid */}
      <section className="agents-section">
        <h2>Active Agents</h2>
        <div className="agents-grid">
          {agents.map(agent => (
            <div
              key={agent.role}
              className={`agent-card ${selectedAgent === agent.role ? 'selected' : ''}`}
              onClick={() => setSelectedAgent(agent.role)}
            >
              <div className="agent-icon">{getAgentIcon(agent.role)}</div>
              <div className="agent-info">
                <h3>{agent.role}</h3>
                <div className={`status-indicator ${getStatusColor(agent.status)}`}>
                  {agent.status === 'running' && <span className="spinner-sm"></span>}
                  {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                </div>
              </div>
              {agent.current_task && (
                <div className="current-task">
                  <small>Current:</small> {agent.current_task}
                </div>
              )}
              {agent.confidence !== null && (
                <div className="confidence-bar">
                  <div className="bar" style={{ width: `${agent.confidence}%` }}></div>
                  <span>{agent.confidence}%</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Decision Log */}
      <section className="decisions-section">
        <h2>Recent Decisions</h2>
        <div className="decision-log">
          {recentDecisions.length === 0 ? (
            <div className="empty-log">
              <span>📋</span>
              <p>No decisions recorded yet</p>
              <small>Decisions will appear here as agents make them</small>
            </div>
          ) : (
            recentDecisions.map(decision => (
              <div key={decision.id} className="decision-item">
                <div className="decision-header">
                  <span className="agent-badge">{decision.agent_role}</span>
                  <span className="decision-type">{decision.decision_type}</span>
                  <span className="timestamp">
                    {new Date(decision.created_at).toLocaleTimeString()}
                  </span>
                </div>
                <div className="decision-content">
                  <p className="recommendation">{decision.recommendation}</p>
                  <p className="reasoning">{decision.reasoning}</p>
                </div>
                <div className="decision-footer">
                  <span className={`confidence ${decision.confidence >= 70 ? 'high' : 'low'}`}>
                    Confidence: {decision.confidence}%
                  </span>
                  {decision.requires_human_review && (
                    <span className="review-required">⚠️ Human Review Required</span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* Task Timeline */}
      <section className="timeline-section">
        <h2>Task Execution Timeline</h2>
        <div className="timeline">
          {taskTimeline.length === 0 ? (
            <div className="empty-timeline">
              <p>No task executions to display</p>
            </div>
          ) : (
            taskTimeline.map(task => (
              <div key={task.id} className={`timeline-item ${task.status}`}>
                <div className="timeline-marker"></div>
                <div className="timeline-content">
                  <div className="task-header">
                    <span className="task-agent">{task.agent_role}</span>
                    <span className="task-action">{task.action}</span>
                  </div>
                  <div className="task-meta">
                    <span>{new Date(task.started_at).toLocaleTimeString()}</span>
                    {task.duration_ms && <span>{task.duration_ms}ms</span>}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      <style>{`
        .agent-monitor {
          max-width: 1400px;
          margin: 0 auto;
          padding: 2rem;
        }
        
        .monitor-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 2rem;
        }
        
        .monitor-header h1 {
          font-size: 2rem;
          font-weight: 700;
        }
        
        .subtitle {
          color: var(--text-secondary, #6b7280);
          flex: 1;
        }
        
        .live-indicator {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          background: #d1fae5;
          color: #065f46;
          border-radius: 9999px;
          font-size: 0.875rem;
          font-weight: 500;
        }
        
        .pulse {
          width: 8px;
          height: 8px;
          background: #10b981;
          border-radius: 50%;
          animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(1.5); }
        }
        
        .agents-section h2,
        .decisions-section h2,
        .timeline-section h2 {
          font-size: 1.25rem;
          font-weight: 600;
          margin-bottom: 1rem;
        }
        
        .agents-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 1rem;
          margin-bottom: 2rem;
        }
        
        .agent-card {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
          cursor: pointer;
          transition: all 0.2s;
          border: 2px solid transparent;
        }
        
        .agent-card:hover {
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .agent-card.selected {
          border-color: var(--primary, #6366f1);
        }
        
        .agent-icon {
          font-size: 2rem;
          margin-bottom: 0.75rem;
        }
        
        .agent-info h3 {
          font-weight: 600;
          margin-bottom: 0.5rem;
        }
        
        .status-indicator {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 500;
        }
        
        .status-idle { background: #f3f4f6; color: #6b7280; }
        .status-running { background: #dbeafe; color: #1d4ed8; }
        .status-waiting { background: #fef3c7; color: #92400e; }
        .status-completed { background: #d1fae5; color: #065f46; }
        .status-failed { background: #fee2e2; color: #991b1b; }
        
        .spinner-sm {
          width: 12px;
          height: 12px;
          border: 2px solid currentColor;
          border-top-color: transparent;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        
        .current-task {
          margin-top: 0.75rem;
          padding: 0.5rem;
          background: var(--bg-secondary, #f9fafb);
          border-radius: 6px;
          font-size: 0.875rem;
        }
        
        .current-task small {
          color: var(--text-secondary, #6b7280);
        }
        
        .confidence-bar {
          margin-top: 0.75rem;
          height: 8px;
          background: #e5e7eb;
          border-radius: 4px;
          position: relative;
        }
        
        .confidence-bar .bar {
          height: 100%;
          background: linear-gradient(90deg, #6366f1, #8b5cf6);
          border-radius: 4px;
        }
        
        .confidence-bar span {
          position: absolute;
          right: 0;
          top: -20px;
          font-size: 0.75rem;
          color: var(--text-secondary, #6b7280);
        }
        
        .decision-log {
          background: white;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
          max-height: 400px;
          overflow-y: auto;
          margin-bottom: 2rem;
        }
        
        .empty-log, .empty-timeline {
          text-align: center;
          padding: 3rem;
          color: var(--text-secondary, #6b7280);
        }
        
        .empty-log span {
          font-size: 2rem;
          display: block;
          margin-bottom: 0.5rem;
        }
        
        .decision-item {
          padding: 1rem 1.5rem;
          border-bottom: 1px solid var(--border-color, #e5e7eb);
        }
        
        .decision-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 0.5rem;
        }
        
        .agent-badge {
          background: var(--primary, #6366f1);
          color: white;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: 500;
        }
        
        .decision-type {
          color: var(--text-secondary, #6b7280);
          font-size: 0.875rem;
        }
        
        .timestamp {
          margin-left: auto;
          color: var(--text-secondary, #6b7280);
          font-size: 0.75rem;
        }
        
        .recommendation {
          font-weight: 500;
          margin-bottom: 0.25rem;
        }
        
        .reasoning {
          color: var(--text-secondary, #6b7280);
          font-size: 0.875rem;
        }
        
        .decision-footer {
          display: flex;
          gap: 1rem;
          margin-top: 0.75rem;
          font-size: 0.75rem;
        }
        
        .confidence.high { color: #065f46; }
        .confidence.low { color: #dc2626; }
        
        .review-required {
          color: #dc2626;
          font-weight: 500;
        }
        
        .timeline {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .timeline-item {
          display: flex;
          gap: 1rem;
          padding: 1rem 0;
          border-left: 2px solid #e5e7eb;
          margin-left: 8px;
          padding-left: 1.5rem;
          position: relative;
        }
        
        .timeline-marker {
          position: absolute;
          left: -6px;
          top: 1.25rem;
          width: 12px;
          height: 12px;
          background: var(--primary, #6366f1);
          border-radius: 50%;
          border: 2px solid white;
        }
        
        .timeline-item.completed .timeline-marker { background: #10b981; }
        .timeline-item.failed .timeline-marker { background: #ef4444; }
        
        .task-header {
          display: flex;
          gap: 0.5rem;
        }
        
        .task-agent {
          font-weight: 500;
        }
        
        .task-action {
          color: var(--text-secondary, #6b7280);
        }
        
        .task-meta {
          display: flex;
          gap: 1rem;
          font-size: 0.75rem;
          color: var(--text-secondary, #6b7280);
          margin-top: 0.25rem;
        }
      `}</style>
    </div>
  );
};

export default AgentMonitor;
