"""Initial schema - all tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('role', sa.String(50), nullable=False, default='consumer'),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Partners table
    op.create_table(
        'partners',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('api_key_hash', sa.String(255), nullable=False),
        sa.Column('webhook_url', sa.String(500)),
        sa.Column('allowed_programs', postgresql.JSONB),
        sa.Column('branding', postgresql.JSONB),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Cases table
    op.create_table(
        'cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('consumer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('status', sa.String(50), nullable=False, default='draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('submitted_at', sa.DateTime(timezone=True)),
    )
    
    # Intake drafts
    op.create_table(
        'intake_drafts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cases.id'), nullable=False, unique=True),
        sa.Column('data', postgresql.JSONB),
        sa.Column('provenance', postgresql.JSONB),
        sa.Column('current_chapter', sa.Integer, default=1),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Intake snapshots
    op.create_table(
        'intake_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cases.id'), nullable=False, index=True),
        sa.Column('data', postgresql.JSONB, nullable=False),
        sa.Column('provenance', postgresql.JSONB),
        sa.Column('data_hash', sa.String(64), nullable=False),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Consents
    op.create_table(
        'consents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('consumer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cases.id')),
        sa.Column('scope', sa.String(100), nullable=False),
        sa.Column('provider', sa.String(100), nullable=False),
        sa.Column('purpose', sa.Text, nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='requested'),
        sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('granted_at', sa.DateTime(timezone=True)),
        sa.Column('revoked_at', sa.DateTime(timezone=True)),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Access logs
    op.create_table(
        'access_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('consumer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('accessor_id', postgresql.UUID(as_uuid=True)),
        sa.Column('accessor_type', sa.String(50), nullable=False),
        sa.Column('accessor_role', sa.String(50)),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True)),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('purpose', sa.Text),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Programs
    op.create_table(
        'programs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('program_type', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('config', postgresql.JSONB),
        sa.Column('version', sa.Integer, default=1, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Scenario runs
    op.create_table(
        'scenario_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cases.id'), nullable=False, index=True),
        sa.Column('intake_snapshot_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('intake_snapshots.id'), nullable=False),
        sa.Column('total_scenarios', sa.Integer, nullable=False),
        sa.Column('eligible_count', sa.Integer),
        sa.Column('refer_count', sa.Integer),
        sa.Column('not_eligible_count', sa.Integer),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Scenarios
    op.create_table(
        'scenarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scenario_runs.id'), nullable=False, index=True),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('programs.id'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('confidence_score', sa.Integer),
        sa.Column('pricing', postgresql.JSONB),
        sa.Column('reason_codes', postgresql.JSONB),
        sa.Column('verify_checklist', postgresql.JSONB),
        sa.Column('explanation', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Audit events
    op.create_table(
        'audit_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True)),
        sa.Column('actor_role', sa.String(50)),
        sa.Column('resource_type', sa.String(100)),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True)),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('details', postgresql.JSONB),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
    )
    
    # Create indexes
    op.create_index('ix_audit_events_actor', 'audit_events', ['actor_id'])
    op.create_index('ix_audit_events_resource', 'audit_events', ['resource_type', 'resource_id'])
    op.create_index('ix_consents_status', 'consents', ['status'])
    op.create_index('ix_scenarios_status', 'scenarios', ['status'])


def downgrade() -> None:
    op.drop_table('audit_events')
    op.drop_table('scenarios')
    op.drop_table('scenario_runs')
    op.drop_table('programs')
    op.drop_table('access_logs')
    op.drop_table('consents')
    op.drop_table('intake_snapshots')
    op.drop_table('intake_drafts')
    op.drop_table('cases')
    op.drop_table('partners')
    op.drop_table('users')
