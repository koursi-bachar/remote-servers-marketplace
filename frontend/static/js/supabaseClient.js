export const SUPABASE_URL = "https://vtdfrecfwgqrtiodrlnj.supabase.co";
export const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0ZGZyZWNmd2dxcnRpb2RybG5qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNzExNTYsImV4cCI6MjA3ODY0NzE1Nn0.4fiWf5x9ACJdXr6OCLetr1fOKXwv-0ChYZDoY-Bm1kI";

// Create Supabase client once for entire app
export const supabase = window.supabase.createClient(
    SUPABASE_URL,
    SUPABASE_ANON_KEY
);