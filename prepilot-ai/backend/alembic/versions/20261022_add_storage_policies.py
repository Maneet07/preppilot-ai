"""Add Storage Bucket and Policies Migration for PrepPilot AI

Revision ID: 20261022_add_storage_policies
Create Date: 2026-10-22 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "20261022_add_storage_policies"
down_revision = "20261021_add_rls_policies"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create private resumes bucket and storage policies."""

    # Create the resumes bucket (if not already exists)
    # This is a private bucket for user resume storage
    op.execute(
        "INSERT INTO storage.buckets (id, name, public) "
        "VALUES ('resumes', 'resumes', false) "
        "ON CONFLICT (id) DO NOTHING;"
    )

    # Storage Policies for Resumes
    # All policies ensure the first path segment matches the authenticated user's ID
    # Resumes are never publicly accessible

    # PUBLIC: Allow authenticated users to view their own resumes
    op.execute(
        "CREATE POLICY \"Users can view own resume files\" ON storage.objects "
        "FOR SELECT USING (\n"
        "    bucket_id = 'resumes' AND "
        "    (storage.foldername(name))[1] = (current_setting('jwt.claims'))->>'sub'\n"
        ");"
    )

    # PUBLIC: Allow authenticated users to upload resumes
    op.execute(
        "CREATE POLICY \"Users can upload resumes\" ON storage.objects "
        "FOR INSERT WITH CHECK (\n"
        "    bucket_id = 'resumes' AND "
        "    (storage.foldername(name))[1] = (current_setting('jwt.claims'))->>'sub' AND "
        "    (name LIKE '%.pdf' OR name LIKE '%.docx' OR name LIKE '%.doc')\n"
        ");"
    )

    # PUBLIC: Allow users to replace their own resumes
    op.execute(
        "UPDATE ON storage.objects "
        "FOR UPDATE USING (\n"
        "    bucket_id = 'resumes' AND "
        "    (storage.foldername(name))[1] = (current_setting('jwt.claims'))->>'sub'\n"
        ");"
    )

    # PUBLIC: Allow users to delete their own resumes
    op.execute(
        "DELETE ON storage.objects "
        "USING (\n"
        "    bucket_id = 'resumes' AND "
        "    (storage.foldername(name))[1] = (current_setting('jwt.claims'))->>'sub'\n"
        ");"
    )

    # Ensure row-level security is enabled on storage.objects
    op.execute("ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;")

    # Grant necessary permissions to authenticated role
    op.execute("GRANT ALL ON storage.objects TO authenticated;")
    op.execute("GRANT SELECT ON storage.buckets TO authenticated;")


def downgrade() -> None:
    """Drop storage policies and bucket."""

    # Drop all storage policies
    op.execute("DROP POLICY IF EXISTS \"Users can view own resume files\" ON storage.objects;")
    op.execute("DROP POLICY IF EXISTS \"Users can upload resumes\" ON storage.objects;")
    op.execute("DROP POLICY IF EXISTS \"Users can update own resume files\" ON storage.objects;")
    op.execute("DROP POLICY IF EXISTS \"Users can delete own resume files\" ON storage.objects;")

    # Disable row-level security on storage.objects
    op.execute("ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;")

    # Revoke permissions from authenticated role
    op.execute("REVOKE ALL ON storage.objects TO authenticated;")
    op.execute("REVOKE SELECT ON storage.buckets TO authenticated;")

    # Drop the resumes bucket
    op.execute("DELETE FROM storage.buckets WHERE id = 'resumes';")