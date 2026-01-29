"""create aeo scores

Revision ID: 001_aeo_scores
Revises: 
Create Date: 2026-01-29 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_aeo_scores'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('aeo_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), nullable=False),
        sa.Column('run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rubric_version', sa.Text(), nullable=False),
        sa.Column('aeo_total', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('aeo_answerability', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('aeo_structure', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('aeo_specificity', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('aeo_trust', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('aeo_coverage', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('aeo_freshness', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('aeo_readability', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.CheckConstraint('aeo_total >= 0 AND aeo_total <= 100', name='chk_aeo_total'),
        sa.ForeignKeyConstraint(['run_id'], ['evaluation_runs.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('run_id', name='uq_aeo_run_id')
    )
    op.create_index('idx_aeo_scores_run_id', 'aeo_scores', ['run_id'], unique=False)


def downgrade():
    op.drop_index('idx_aeo_scores_run_id', table_name='aeo_scores')
    op.drop_table('aeo_scores')
