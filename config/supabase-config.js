// Supabase configuration for tree photo storage
// Replace these values with your actual Supabase project credentials
// See docs/SUPABASE_SETUP.md for setup instructions

const SUPABASE_CONFIG = {
  // Your Supabase project URL (e.g., https://xxxxx.supabase.co)
  url: 'YOUR-SUPABASE-PROJECT-URL',

  // Your Supabase anon/public key (safe to expose in client-side code)
  anonKey: 'YOUR-SUPABASE-ANON-KEY',

  // Storage bucket name
  bucketName: 'tree-photos',

  // Photo settings
  maxFileSize: 5 * 1024 * 1024, // 5 MB
  allowedTypes: ['image/jpeg', 'image/png', 'image/webp'],
  thumbnailSize: 400 // pixels
};

// Initialize Supabase client (will be used by upload tool and gallery)
let supabaseClient = null;

function initSupabase() {
  if (SUPABASE_CONFIG.url === 'YOUR-SUPABASE-PROJECT-URL') {
    console.warn('Supabase not configured. Please update config/supabase-config.js');
    return null;
  }

  if (typeof supabase === 'undefined') {
    console.error('Supabase library not loaded. Include: <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>');
    return null;
  }

  const { createClient } = supabase;
  supabaseClient = createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey);
  return supabaseClient;
}
