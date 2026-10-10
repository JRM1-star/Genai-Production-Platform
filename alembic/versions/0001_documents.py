from alembic import op
import sqlalchemy as sa

revision = "0001_documents"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False, index=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_documents_tenant_sha",
        "documents",
        ["tenant_id", "sha256"],
        unique=True,
    )

def downgrade():
    op.drop_index("ix_documents_tenant_sha", table_name="documents")
    op.drop_table("documents")
