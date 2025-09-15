"""Multi-source field mappings

Revision ID: 005_multi_source_mappings
Revises: 004_add_mapping_templates
Create Date: 2025-09-12 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '005_multi_source_mappings'
down_revision = '004_add_mapping_templates'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to field_mappings table
    op.add_column('field_mappings', sa.Column('mapping_set_id', sa.String(255), nullable=True))
    op.add_column('field_mappings', sa.Column('source_type', sa.String(50), nullable=True))
    
    # Make source_id nullable for multi-source mappings
    op.alter_column('field_mappings', 'source_id', nullable=True)
    
    # Add new columns to mapping_templates table
    op.add_column('mapping_templates', sa.Column('is_multi_source', sa.Boolean(), default=False))
    op.add_column('mapping_templates', sa.Column('source_types', sa.JSON(), nullable=True))

def downgrade():
    # Remove added columns
    op.drop_column('field_mappings', 'mapping_set_id')
    op.drop_column('field_mappings', 'source_type')
    op.drop_column('mapping_templates', 'is_multi_source')
    op.drop_column('mapping_templates', 'source_types')
    
    # Restore source_id as not nullable
    op.alter_column('field_mappings', 'source_id', nullable=False)