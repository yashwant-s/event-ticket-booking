"""Initial migration with all tables

Revision ID: 001
Revises: 
Create Date: 2026-01-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create events table
    op.create_table('events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('name', sa.String(length=250), nullable=False),
    sa.Column('address', sa.String(length=500), nullable=False),
    sa.Column('event_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('pool_size', sa.Integer(), nullable=False),
    sa.Column('ticket_price', sa.Float(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_owner_id'), 'events', ['owner_id'], unique=False)
    
    # Create event_ticket_pools table
    op.create_table('event_ticket_pools',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('ticket_count', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_ticket_pools_event_id'), 'event_ticket_pools', ['event_id'], unique=False)
    
    # Create tickets table
    op.create_table('tickets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('booked', 'cancelled', 'pending', name='ticketstatus'), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tickets_event_id'), 'tickets', ['event_id'], unique=False)
    op.create_index(op.f('ix_tickets_user_id'), 'tickets', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_tickets_user_id'), table_name='tickets')
    op.drop_index(op.f('ix_tickets_event_id'), table_name='tickets')
    op.drop_table('tickets')
    op.drop_index(op.f('ix_event_ticket_pools_event_id'), table_name='event_ticket_pools')
    op.drop_table('event_ticket_pools')
    op.drop_index(op.f('ix_events_owner_id'), table_name='events')
    op.drop_table('events')
