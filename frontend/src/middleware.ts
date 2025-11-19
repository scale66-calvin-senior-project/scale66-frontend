import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Middleware for route protection and authentication
 * 
 * TODO: Implement authentication check
 * - Check for auth token in cookies/headers
 * - Validate token with Firebase Auth
 * - Redirect unauthenticated users to /login
 */
export function middleware(_request: NextRequest) {
  // TODO: Implement auth check
  // const token = _request.cookies.get('auth-token');
  // if (!token) {
  //   return NextResponse.redirect(new URL('/login', _request.url));
  // }
  
  return NextResponse.next();
}

/**
 * Configure which routes require authentication
 * All routes under (app) route group require authentication
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

