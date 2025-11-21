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
		return null;
	}
	return user;
};

/**
 * Get JWT access token for API calls
 * Use this to add Authorization header to backend requests
 */
export const getAccessToken = async (): Promise<string | null> => {
	const session = await getSession();
	return session?.access_token || null;
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
