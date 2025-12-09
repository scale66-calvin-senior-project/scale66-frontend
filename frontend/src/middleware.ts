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
  const hasAuthCookie = allCookies.some(cookie => {
    const name = cookie.name.toLowerCase();
    return name.includes('supabase') || 
           name.includes('auth-token') ||
           name.startsWith('sb-');
  });

  // If no auth cookies found, redirect to landing page
  if (!hasAuthCookie) {
    const url = request.nextUrl.clone();
    url.pathname = '/';
    return NextResponse.redirect(url);
  }

  // Allow through - client-side will validate session properly
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

