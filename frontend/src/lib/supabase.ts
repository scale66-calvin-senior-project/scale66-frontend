/**
 * Supabase Client - Minimal setup for frontend authentication only
 * 
 * ⚠️ IMPORTANT: This client is ONLY for authentication operations!
 * All database queries, storage operations, and business logic
 * should go through the backend API.
 * 
 * Usage:
 * - supabase.auth.signUp()
 * - supabase.auth.signInWithPassword()
 * - supabase.auth.signOut()
 * - supabase.auth.getSession()
 * - supabase.auth.onAuthStateChange()
 * 
 * ❌ DO NOT USE:
 * - supabase.from('table').select() → Use backend API instead
 * - supabase.storage.upload() → Use backend API instead
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Missing Supabase environment variables. ' +
    'Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local'
  )
}

// Create Supabase client with auth-only configuration
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    storage: typeof window !== 'undefined' ? window.localStorage : undefined,
  },
})

/**
 * Get current session
 * Returns the active session with JWT token
 */
export const getSession = async () => {
  const { data: { session }, error } = await supabase.auth.getSession()
  if (error) {
    console.error('Error getting session:', error)
    return null
  }
  return session
}

/**
 * Get JWT access token for API calls
 * Use this to add Authorization header to backend requests
 */
export const getAccessToken = async () => {
  const session = await getSession()
  return session?.access_token || null
}

/**
 * Sign out user
 */
export const signOut = async () => {
  const { error } = await supabase.auth.signOut()
  if (error) {
    console.error('Error signing out:', error)
    throw error
  }
}

export default supabase

