-- ============================================================
-- Supabase Storage Bucket for Resumes
-- Creates a private bucket for user resume storage
-- Organizes objects using user-specific path: <authenticated-user-uuid>/<unique-file-id>.pdf
-- ============================================================

-- Create the resumes bucket (if not already exists)
-- This is a private bucket for user resume storage
INSERT INTO storage.buckets (id, name, public)
VALUES ('resumes', 'resumes', false)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- Storage Policies for Resumes
-- All policies ensure the first path segment matches the authenticated user's ID
-- Resumes are never publicly accessible
-- ============================================================

-- ============================
-- PUBLIC: Allow authenticated users to view their own resumes
-- ============================

-- Allow authenticated users to fetch their own resume files
-- Path must start with their user UUID
CREATE POLICY "Users can view own resume files" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'resumes' AND
        (storage.foldername(name))[1] = (current_setting('jwt.claims'))->>'sub'
    );

-- ============================
-- PUBLIC: Allow authenticated users to upload resumes
-- ============================

-- Allow authenticated users to upload resume files
-- Path: <user-uuid>/<unique-file-id>.pdf
-- Validates that the first path segment matches the authenticated user's ID
CREATE POLICY "Users can upload resumes" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'resumes' AND
        (storage.foldername(name))[1] = (current_setting('jwt.claims'))->>'sub' AND
        (name LIKE '%.pdf' OR name LIKE '%.docx' OR name LIKE '%.doc')
    );

-- ============================
-- PUBLIC: Allow users to replace their own resumes
-- ============================

-- Allow users to update their own resume files
UPDATE ON storage.objects
FOR UPDATE USING (
    bucket_id = 'resumes' AND
    (storage.foldername(name))[1] = (current_setting('jwt.claims'))->>'sub'
);

-- ============================
-- PUBLIC: Allow users to delete their own resumes
-- ============================

-- Allow users to delete their own resume files
DELETE ON storage.objects
USING (
    bucket_id = 'resumes' AND
    (storage.foldername(name))[1] = (current_setting('jwt.claims'))->>'sub'
);

-- ============================
-- Ensure row-level security is enabled on storage.objects
-- ============================

ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- ============================
-- Grant necessary permissions to authenticated role
-- ============================

GRANT ALL ON storage.objects TO authenticated;
GRANT SELECT ON storage.buckets TO authenticated;