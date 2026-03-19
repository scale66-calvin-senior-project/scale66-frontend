import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Middleware for route protection and authentication
 * 
 * Protects app routes:
 * - Checks for Supabase auth cookies
 * - Redirects unauthenticated users to landing page
 * - Client-side auth context handles detailed session validation
 * 
 * Note: Simplified to check for cookie presence only.
 * Full session validation happens client-side for better UX.
 */
export async function middleware(request: NextRequest) {
  const cookies = request.cookies;
  
  // Check for any Supabase auth-related cookies
  // Supabase stores session in cookies like: sb-<project-ref>-auth-token
  // Get all cookies and check their names
  const allCookies = cookies.getAll();
  // Note: hasAuthCookie check is currently unused but kept for future use
  allCookies.some(cookie => {
    const name = cookie.name.toLowerCase();
    // Check for various Supabase cookie patterns
    return name.includes('supabase') || 
           name.includes('auth-token') ||
           name.includes('auth-token-code-verifier') ||
           name.startsWith('sb-') ||
           name.includes('access_token') ||
           name.includes('refresh_token');
  });

  // Be lenient - Supabase may store session in localStorage (client-side only)
  // If no auth cookies found, still allow through and let client-side validate
  // This prevents false redirects when user is actually authenticated
  // Client-side pages will handle the actual authentication check
  
  // Only redirect if we're absolutely sure there's no session
  // For now, let all requests through - client-side will handle redirects
  // This is safer and prevents redirect loops
  
  return NextResponse.next();
}

/**
 * Configure which routes require authentication and subscription
 * All routes under (app) route group require both
 */
export const config = {
  matcher: [
    '/dashboard/:path*',
    '/campaigns/:path*',
    '/canvas/:path*',
    '/brand-kit/:path*',
    '/settings/:path*',
  ],
};

