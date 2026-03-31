/**
 * Supabase Client - Minimal setup for frontend authentication only
 */

import { createClient } from "@supabase/supabase-js";
import type { Session, User } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
	throw new Error("Missing Supabase environment variables. " + "Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local");
}

// Create Supabase client with auth-only configuration
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
	auth: {
		autoRefreshToken: true,
		persistSession: true,
		detectSessionInUrl: true,
		storage: typeof window !== "undefined" ? window.localStorage : undefined,
	},
});

// Export types for convenience
export type { Session, User };

// ── Auth-ready gate ───────────────────────────────────────────────────────────
// Supabase initializes asynchronously. On first load it fires INITIAL_SESSION
// once it has restored (and optionally refreshed) the session from localStorage.
// API calls made before this event receive no token and return 403.
//
// We create a single module-level promise that resolves with the access token
// (or null) as soon as INITIAL_SESSION fires. getAccessToken() awaits it so
// the very first call blocks until auth is ready. After that the promise is
// already resolved so subsequent calls pay no cost.

const _authReady: Promise<string | null> =
	typeof window === 'undefined'
		? // Server-side: no localStorage, no session — resolve immediately
		  Promise.resolve(null)
		: new Promise<string | null>((resolve) => {
				let settled = false;

				const settle = (token: string | null) => {
					if (settled) return;
					settled = true;
					subscription.unsubscribe();
					resolve(token);
				};

				const { data: { subscription } } = supabase.auth.onAuthStateChange(
					(event, session) => {
						if (event === 'INITIAL_SESSION') {
							if (session?.access_token) {
								// Valid session ready — resolve immediately.
								settle(session.access_token);
							} else {
								// INITIAL_SESSION with null means either the user is logged
								// out OR the access token is expired and Supabase is
								// refreshing it in the background (TOKEN_REFRESHED follows).
								// Wait up to 800 ms for the refresh before giving up.
								setTimeout(() => settle(null), 800);
							}
						} else if (event === 'TOKEN_REFRESHED' || event === 'SIGNED_IN') {
							settle(session?.access_token ?? null);
						}
					}
				);

				// Hard ceiling: unblock after 3 s if no auth event fires at all.
				setTimeout(() => settle(null), 3000);
		  });

/**
 * Get current session
 * Returns the active session with JWT token
 */
export const getSession = async (): Promise<Session | null> => {
	const {
		data: { session },
		error,
	} = await supabase.auth.getSession();
	if (error) {
		console.error("Error getting session:", error);
		// If JWT contains invalid user ID, clear the session
		if (error.message?.includes('sub claim') || error.message?.includes('does not exist')) {
			console.error('JWT contains invalid user ID - clearing session');
			await supabase.auth.signOut();
		}
		return null;
	}
	return session;
};

/**
 * Get current user
 * Returns the authenticated user or null
 */
export const getCurrentUser = async (): Promise<User | null> => {
	const {
		data: { user },
		error,
	} = await supabase.auth.getUser();
	if (error) {
		console.error("Error getting user:", error);
		// If JWT contains invalid user ID, clear the session
		if (error.message?.includes('sub claim') || error.message?.includes('does not exist')) {
			console.error('JWT contains invalid user ID - clearing session');
			await supabase.auth.signOut();
		}
		return null;
	}
	return user;
};

/**
 * Get JWT access token for API calls
 * Use this to add Authorization header to backend requests
 */
export const getAccessToken = async (): Promise<string | null> => {
	// Await the auth-ready gate. On first call this blocks until INITIAL_SESSION
	// fires. On every subsequent call the promise is already resolved — zero cost.
	const initialToken = await _authReady;

	// Always read the current session after init so we get a fresh token even
	// after Supabase auto-refreshes it mid-session.
	const session = await getSession();

	// Prefer the live session token. Fall back to the token captured at
	// INITIAL_SESSION in the rare edge-case where getSession() returns null
	// momentarily right after the event fires (Supabase internal state lag).
	return session?.access_token ?? initialToken ?? null;
};

/**
 * Sign up new user with email and password
 */
export const signUp = async (email: string, password: string) => {
	const { data, error } = await supabase.auth.signUp({
		email,
		password,
	});

	if (error) {
		console.error("Error signing up:", error);
		throw error;
	}

	return data;
};

/**
 * Sign in with email and password
 */
export const signInWithPassword = async (email: string, password: string) => {
	const { data, error } = await supabase.auth.signInWithPassword({
		email,
		password,
	});

	if (error) {
		console.error("Error signing in:", error);
		throw error;
	}

	return data;
};

/**
 * Sign in with OAuth provider (Google, GitHub, etc.)
 */
export const signInWithOAuth = async (provider: "google" | "github" | "apple") => {
	const { data, error } = await supabase.auth.signInWithOAuth({
		provider,
		options: {
			redirectTo: `${window.location.origin}/dashboard`,
		},
	});

	if (error) {
		console.error("Error signing in with OAuth:", error);
		throw error;
	}

	return data;
};

/**
 * Sign out user
 */
export const signOut = async () => {
	const { error } = await supabase.auth.signOut();
	if (error) {
		console.error("Error signing out:", error);
		throw error;
	}
};

/**
 * Reset password - Send password reset email
 */
export const resetPassword = async (email: string) => {
	const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
		redirectTo: `${window.location.origin}/reset-password`,
	});

	if (error) {
		console.error("Error sending reset password email:", error);
		throw error;
	}

	return data;
};

/**
 * Update user password
 */
export const updatePassword = async (newPassword: string) => {
	const { data, error } = await supabase.auth.updateUser({
		password: newPassword,
	});

	if (error) {
		console.error("Error updating password:", error);
		throw error;
	}

	return data;
};

export default supabase;
