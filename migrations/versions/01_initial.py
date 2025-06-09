"""Initial migration

Revision ID: 01_initial
Revises: 
Create Date: 2025-05-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create Role table
    op.create_table('role',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create User table
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_password_change', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create OTPVerification table
    op.create_table('otp_verification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('otp_code', sa.String(length=6), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('verified', sa.Boolean(), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_otp_verification_email'), 'otp_verification', ['email'], unique=False)
    
    # Create RateLimit table
    op.create_table('rate_limit',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=True),
        sa.Column('reset_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rate_limit_key'), 'rate_limit', ['key'], unique=False)


def downgrade():
    # Drop tables in reverse order of creation
    op.drop_index(op.f('ix_rate_limit_key'), table_name='rate_limit')
    op.drop_table('rate_limit')
    op.drop_index(op.f('ix_otp_verification_email'), table_name='otp_verification')
    op.drop_table('otp_verification')
    op.drop_table('user')
    op.drop_table('role')