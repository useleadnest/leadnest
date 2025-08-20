"""Launch Multiplier Migration - Add comprehensive tables for onboarding, ROI, integrations, agency mode, and AI scoring

Revision ID: launch_multiplier_v1
Revises: 
Create Date: 2025-01-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'launch_multiplier_v1'
down_revision = 'f01fb9e06ec7'  # Points to the init migration
branch_labels = None
depends_on = None


def upgrade():
    """Add all new tables and columns for Launch Multiplier features (SQLite compatible)"""
    
    # Create users table (SQLite compatible - no ENUM types)
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=True),  # owner, agency_owner, agency_member, admin
        sa.Column('agency_id', sa.Integer(), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=100), nullable=True),
        sa.Column('subscription_status', sa.String(length=20), nullable=True),  # trial, active, past_due, canceled, unpaid
        sa.Column('trial_ends_at', sa.DateTime(), nullable=True),
        sa.Column('subscription_ends_at', sa.DateTime(), nullable=True),
        sa.Column('business_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['agency_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('stripe_customer_id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    
    # Update businesses table with new columns (SQLite compatible)
    with op.batch_alter_table('businesses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('owner_email', sa.String(length=255), nullable=False, server_default='owner@example.com'))
        batch_op.add_column(sa.Column('twilio_account_sid', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('twilio_auth_token', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('twilio_phone_number', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('calendly_url', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('avg_deal_size', sa.Numeric(precision=10, scale=2), nullable=True))
        batch_op.add_column(sa.Column('close_rate', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('cost_per_lead', sa.Numeric(precision=10, scale=2), nullable=True))
    
    # Update leads table with enhanced fields (SQLite compatible)
    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('first_name', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('last_name', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('company', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('title', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('score', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('priority', sa.String(length=20), nullable=True, server_default='medium'))
        batch_op.add_column(sa.Column('last_contacted_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('next_followup_at', sa.DateTime(), nullable=True))
        batch_op.create_index('ix_leads_business_status', ['business_id', 'status'], unique=False)
        batch_op.create_index('ix_leads_business_score', ['business_id', 'score'], unique=False)
        batch_op.create_index('ix_leads_phone_email', ['phone', 'email'], unique=False)
        batch_op.create_index(op.f('ix_leads_phone'), ['phone'], unique=False)
        batch_op.create_index(op.f('ix_leads_email'), ['email'], unique=False)
    
    # Update conversations table (SQLite compatible)
    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=True, server_default='active'))
        batch_op.add_column(sa.Column('subject', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('last_message_at', sa.DateTime(), nullable=True))
        batch_op.create_index('ix_conversations_lead_channel', ['lead_id', 'channel'], unique=False)
    
    # Update messages table (SQLite compatible)
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('message_type', sa.String(length=20), nullable=True, server_default='text'))
        batch_op.add_column(sa.Column('external_id', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=True, server_default='sent'))
        batch_op.add_column(sa.Column('extra_data', sa.JSON(), nullable=True))
        batch_op.create_index('ix_messages_conversation_ts', ['conversation_id', 'ts'], unique=False)
    
    # Update bookings table (SQLite compatible)
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('ends_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=True, server_default='scheduled'))
        batch_op.add_column(sa.Column('booking_type', sa.String(length=50), nullable=True, server_default='consultation'))
        batch_op.add_column(sa.Column('external_id', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('show_status', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('outcome', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('revenue_generated', sa.Numeric(precision=10, scale=2), nullable=True))
        batch_op.create_index('ix_bookings_business_starts_at', ['business_id', 'starts_at'], unique=False)
        batch_op.create_index('ix_bookings_lead_starts_at', ['lead_id', 'starts_at'], unique=False)
    
    # Update idempotency_keys table (SQLite compatible)
    with op.batch_alter_table('idempotency_keys', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('expires_at', sa.DateTime(), nullable=True))

    # Create onboarding_progress table
    op.create_table('onboarding_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('step', sa.String(length=50), nullable=False),  # connect_twilio, import_csv, enable_auto_reply, send_test_sms, connect_calendly
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'step', name='unique_user_step')
    )
    
    # Create roi_reports table
    op.create_table('roi_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('leads_received', sa.Integer(), nullable=True),
        sa.Column('leads_responded', sa.Integer(), nullable=True),
        sa.Column('calls_booked', sa.Integer(), nullable=True),
        sa.Column('deals_closed', sa.Integer(), nullable=True),
        sa.Column('estimated_revenue', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('total_cost', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('roi_percentage', sa.Float(), nullable=True),
        sa.Column('pdf_url', sa.String(length=500), nullable=True),
        sa.Column('emailed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create integrations table
    op.create_table('integrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),  # zapier, slack, calendly, twilio
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('webhook_url', sa.String(length=500), nullable=True),
        sa.Column('api_key', sa.String(length=255), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('last_triggered_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_id', 'type', 'name', name='unique_business_integration')
    )
    
    # Create nurture_sequences table
    op.create_table('nurture_sequences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('vertical', sa.String(length=50), nullable=True),
        sa.Column('steps', sa.JSON(), nullable=False),
        sa.Column('total_sent', sa.Integer(), nullable=True),
        sa.Column('total_opened', sa.Integer(), nullable=True),
        sa.Column('total_replied', sa.Integer(), nullable=True),
        sa.Column('total_booked', sa.Integer(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create nurture_executions table
    op.create_table('nurture_executions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('sequence_id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('current_step', sa.Integer(), nullable=True),
        sa.Column('next_action_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('stopped_at', sa.DateTime(), nullable=True),
        sa.Column('stop_reason', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
        sa.ForeignKeyConstraint(['sequence_id'], ['nurture_sequences.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sequence_id', 'lead_id', name='unique_sequence_lead')
    )
    
    # Create ai_scoring table
    op.create_table('ai_scoring',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('factors', sa.JSON(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('recommended_action', sa.String(length=100), nullable=True),
        sa.Column('best_contact_time', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_id', 'lead_id', name='unique_business_lead_score')
    )
    
    # Create ai_scoring_config table
    op.create_table('ai_scoring_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('recency_weight', sa.Float(), nullable=True),
        sa.Column('source_weight', sa.Float(), nullable=True),
        sa.Column('engagement_weight', sa.Float(), nullable=True),
        sa.Column('profile_completeness_weight', sa.Float(), nullable=True),
        sa.Column('high_value_sources', sa.JSON(), nullable=True),
        sa.Column('peak_contact_hours', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_id')
    )
    
    # Create testimonials table
    op.create_table('testimonials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('author_name', sa.String(length=200), nullable=True),
        sa.Column('author_title', sa.String(length=200), nullable=True),
        sa.Column('star_rating', sa.Integer(), nullable=True),
        sa.Column('public', sa.Boolean(), nullable=True),
        sa.Column('featured', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create activity_logs table
    op.create_table('activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('integration_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add remaining indexes
    op.create_index('ix_roi_reports_business_period', 'roi_reports', ['business_id', 'period_start', 'period_end'], unique=False)
    op.create_index('ix_activity_logs_business_created', 'activity_logs', ['business_id', 'created_at'], unique=False)
    op.create_index('ix_activity_logs_lead', 'activity_logs', ['lead_id', 'created_at'], unique=False)
    
    # Create onboarding_progress table
    op.create_table('onboarding_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('step', sa.String(length=50), nullable=False),  # connect_twilio, import_csv, enable_auto_reply, send_test_sms, connect_calendly
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'step', name='unique_user_step')
    )
    
    # Create roi_reports table
    op.create_table('roi_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('leads_received', sa.Integer(), nullable=True),
        sa.Column('leads_responded', sa.Integer(), nullable=True),
        sa.Column('calls_booked', sa.Integer(), nullable=True),
        sa.Column('deals_closed', sa.Integer(), nullable=True),
        sa.Column('estimated_revenue', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('total_cost', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('roi_percentage', sa.Float(), nullable=True),
        sa.Column('pdf_url', sa.String(length=500), nullable=True),
        sa.Column('emailed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_roi_reports_business_period', 'roi_reports', ['business_id', 'period_start', 'period_end'], unique=False)
    
    # Create integrations table
    op.create_table('integrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),  # zapier, slack, calendly, twilio
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('webhook_url', sa.String(length=500), nullable=True),
        sa.Column('api_key', sa.String(length=255), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('last_triggered_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_id', 'type', 'name', name='unique_business_integration')
    )
    
    # Create nurture_sequences table
    op.create_table('nurture_sequences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('vertical', sa.String(length=50), nullable=True),
        sa.Column('steps', sa.JSON(), nullable=False),
        sa.Column('total_sent', sa.Integer(), nullable=True),
        sa.Column('total_opened', sa.Integer(), nullable=True),
        sa.Column('total_replied', sa.Integer(), nullable=True),
        sa.Column('total_booked', sa.Integer(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create nurture_executions table
    op.create_table('nurture_executions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('sequence_id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('current_step', sa.Integer(), nullable=True),
        sa.Column('next_action_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('stopped_at', sa.DateTime(), nullable=True),
        sa.Column('stop_reason', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
        sa.ForeignKeyConstraint(['sequence_id'], ['nurture_sequences.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sequence_id', 'lead_id', name='unique_sequence_lead')
    )
    
    # Create ai_scoring table
    op.create_table('ai_scoring',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('factors', sa.JSON(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('recommended_action', sa.String(length=100), nullable=True),
        sa.Column('best_contact_time', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_id', 'lead_id', name='unique_business_lead_score')
    )
    
    # Create ai_scoring_config table
    op.create_table('ai_scoring_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('recency_weight', sa.Float(), nullable=True),
        sa.Column('source_weight', sa.Float(), nullable=True),
        sa.Column('engagement_weight', sa.Float(), nullable=True),
        sa.Column('profile_completeness_weight', sa.Float(), nullable=True),
        sa.Column('high_value_sources', sa.JSON(), nullable=True),
        sa.Column('peak_contact_hours', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_id')
    )
    
    # Create testimonials table
    op.create_table('testimonials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('author_name', sa.String(length=200), nullable=True),
        sa.Column('author_title', sa.String(length=200), nullable=True),
        sa.Column('star_rating', sa.Integer(), nullable=True),
        sa.Column('public', sa.Boolean(), nullable=True),
        sa.Column('featured', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create activity_logs table
    op.create_table('activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('integration_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_activity_logs_business_created', 'activity_logs', ['business_id', 'created_at'], unique=False)
    op.create_index('ix_activity_logs_lead', 'activity_logs', ['lead_id', 'created_at'], unique=False)


def downgrade():
    """Remove all Launch Multiplier tables and columns"""
    
    # Drop indexes first
    op.drop_index('ix_activity_logs_lead', table_name='activity_logs')
    op.drop_index('ix_activity_logs_business_created', table_name='activity_logs')
    op.drop_index('ix_roi_reports_business_period', table_name='roi_reports')
    op.drop_index('ix_messages_conversation_ts', table_name='messages')
    op.drop_index('ix_conversations_lead_channel', table_name='conversations')
    op.drop_index('ix_bookings_lead_starts_at', table_name='bookings')
    op.drop_index('ix_bookings_business_starts_at', table_name='bookings')
    op.drop_index('ix_leads_phone_email', table_name='leads')
    op.drop_index('ix_leads_business_score', table_name='leads')
    op.drop_index('ix_leads_business_status', table_name='leads')
    op.drop_index(op.f('ix_leads_email'), table_name='leads')
    op.drop_index(op.f('ix_leads_phone'), table_name='leads')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    
    # Drop tables
    op.drop_table('activity_logs')
    op.drop_table('testimonials')
    op.drop_table('ai_scoring_config')
    op.drop_table('ai_scoring')
    op.drop_table('nurture_executions')
    op.drop_table('nurture_sequences')
    op.drop_table('integrations')
    op.drop_table('roi_reports')
    op.drop_table('onboarding_progress')
    op.drop_table('users')
    
    # Remove columns from existing tables
    op.drop_column('idempotency_keys', 'expires_at')
    op.drop_column('idempotency_keys', 'updated_at')
    op.drop_column('bookings', 'revenue_generated')
    op.drop_column('bookings', 'outcome')
    op.drop_column('bookings', 'show_status')
    op.drop_column('bookings', 'external_id')
    op.drop_column('bookings', 'booking_type')
    op.drop_column('bookings', 'status')
    op.drop_column('bookings', 'ends_at')
    op.drop_column('bookings', 'updated_at')
    op.drop_column('messages', 'extra_data')
    op.drop_column('messages', 'status')
    op.drop_column('messages', 'external_id')
    op.drop_column('messages', 'message_type')
    op.drop_column('messages', 'updated_at')
    op.drop_column('conversations', 'last_message_at')
    op.drop_column('conversations', 'subject')
    op.drop_column('conversations', 'status')
    op.drop_column('conversations', 'updated_at')
    op.drop_column('leads', 'next_followup_at')
    op.drop_column('leads', 'last_contacted_at')
    op.drop_column('leads', 'priority')
    op.drop_column('leads', 'score')
    op.drop_column('leads', 'notes')
    op.drop_column('leads', 'title')
    op.drop_column('leads', 'company')
    op.drop_column('leads', 'last_name')
    op.drop_column('leads', 'first_name')
    op.drop_column('leads', 'updated_at')
    op.drop_column('businesses', 'cost_per_lead')
    op.drop_column('businesses', 'close_rate')
    op.drop_column('businesses', 'avg_deal_size')
    op.drop_column('businesses', 'calendly_url')
    op.drop_column('businesses', 'twilio_phone_number')
    op.drop_column('businesses', 'twilio_auth_token')
    op.drop_column('businesses', 'twilio_account_sid')
    op.drop_column('businesses', 'owner_email')
    op.drop_column('businesses', 'updated_at')
