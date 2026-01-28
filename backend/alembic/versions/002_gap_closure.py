"""Add pulse, fairness, ruleset tables

Revision ID: 002_gap_closure
Revises: 001_initial
Create Date: 2026-01-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_gap_closure'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add program_code to programs
    op.add_column('programs', sa.Column('program_code', sa.String(50), unique=True))
    
    # Rulesets table
    op.create_table(
        'rulesets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('programs.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('conditions', postgresql.JSONB, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('version', sa.Integer, default=1, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('ix_rulesets_program', 'rulesets', ['program_id'])
    
    # Review tickets table
    op.create_table(
        'review_tickets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('scenario_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scenarios.id')),
        sa.Column('trigger_reason', sa.String(500), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('priority', sa.String(50), nullable=False, default='normal'),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('assigned_at', sa.DateTime(timezone=True)),
        sa.Column('resolved_at', sa.DateTime(timezone=True)),
        sa.Column('resolution', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('ix_review_tickets_status', 'review_tickets', ['status'])
    op.create_index('ix_review_tickets_case', 'review_tickets', ['case_id'])
    
    # Overrides table
    op.create_table(
        'overrides',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('review_tickets.id'), nullable=False),
        sa.Column('scenario_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scenarios.id'), nullable=False),
        sa.Column('original_status', sa.String(50), nullable=False),
        sa.Column('new_status', sa.String(50), nullable=False),
        sa.Column('justification', sa.Text, nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Pulse subscriptions table
    op.create_table(
        'pulse_subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('consumer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('frequency', sa.String(50), nullable=False, default='daily'),
        sa.Column('event_types', postgresql.JSONB, default=[]),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('paused_at', sa.DateTime(timezone=True)),
        sa.Column('consent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('consents.id')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('ix_pulse_subscriptions_consumer', 'pulse_subscriptions', ['consumer_id'])
    
    # Pulse alerts table
    op.create_table(
        'pulse_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('consumer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('pulse_subscriptions.id')),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cases.id')),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('summary', sa.String(500), nullable=False),
        sa.Column('impact', sa.Text),
        sa.Column('suggested_action', sa.Text),
        sa.Column('event_data', postgresql.JSONB),
        sa.Column('scenario_refresh_available', sa.Boolean, default=False, nullable=False),
        sa.Column('scenario_refresh_triggered', sa.Boolean, default=False, nullable=False),
        sa.Column('is_read', sa.Boolean, default=False, nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_pulse_alerts_consumer', 'pulse_alerts', ['consumer_id'])
    op.create_index('ix_pulse_alerts_unread', 'pulse_alerts', ['consumer_id', 'is_read'])
    
    # Fairness tests table
    op.create_table(
        'fairness_tests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('model_version', sa.String(100), nullable=False),
        sa.Column('rules_version', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('disparate_impact_passed', sa.Boolean, default=False, nullable=False),
        sa.Column('feature_audit_passed', sa.Boolean, default=False, nullable=False),
        sa.Column('lda_available', sa.Boolean, default=False, nullable=False),
        sa.Column('disparate_impact_results', postgresql.JSONB),
        sa.Column('feature_audit_result', postgresql.JSONB),
        sa.Column('lda_result', postgresql.JSONB),
        sa.Column('blocking_issues', postgresql.JSONB, default=[]),
        sa.Column('warnings', postgresql.JSONB, default=[]),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('duration_seconds', sa.Float),
        sa.Column('requires_approval', sa.Boolean, default=True, nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approved_at', sa.DateTime(timezone=True)),
        sa.Column('approval_notes', sa.Text),
        sa.Column('deployment_allowed', sa.Boolean, default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('ix_fairness_tests_status', 'fairness_tests', ['status'])
    
    # Reason codes table
    op.create_table(
        'reason_codes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('consumer_message', sa.Text, nullable=False),
        sa.Column('agency_message', sa.Text),
        sa.Column('improvement_guidance', sa.Text),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Audit snapshots table
    op.create_table(
        'audit_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('scenario_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scenario_runs.id'), nullable=False),
        sa.Column('snapshot_type', sa.String(100), nullable=False),
        sa.Column('snapshot_data', postgresql.JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_audit_snapshots_case', 'audit_snapshots', ['case_id'])
    
    # Rankings table
    op.create_table(
        'rankings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scenario_runs.id'), nullable=False),
        sa.Column('mode', sa.String(50), nullable=False),
        sa.Column('ranked_scenario_ids', postgresql.JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Data exports table
    op.create_table(
        'exports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('consumer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('export_type', sa.String(100), nullable=False),
        sa.Column('format', sa.String(50), nullable=False, default='json'),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('file_path', sa.String(500)),
        sa.Column('file_size_bytes', sa.BigInteger),
        sa.Column('download_url', sa.String(500)),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_exports_consumer', 'exports', ['consumer_id'])
    
    # Invites table
    op.create_table(
        'invites',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('inviter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('invitee_email', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('token', sa.String(255), unique=True, nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('accepted_at', sa.DateTime(timezone=True)),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('invites')
    op.drop_table('exports')
    op.drop_table('rankings')
    op.drop_table('audit_snapshots')
    op.drop_table('reason_codes')
    op.drop_table('fairness_tests')
    op.drop_table('pulse_alerts')
    op.drop_table('pulse_subscriptions')
    op.drop_table('overrides')
    op.drop_table('review_tickets')
    op.drop_table('rulesets')
    op.drop_column('programs', 'program_code')
