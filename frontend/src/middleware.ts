import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Middleware for route protection and authentication
 * 
 * TODO: Implement authentication check
 * - Check for Supabase session in cookies
 * - Validate JWT token
 * - Redirect unauthenticated users to /login
 * 
 * Example implementation:
 * ```typescript
 * import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs'
 * 
 * const supabase = createMiddlewareClient({ req: _request, res: response })
 * const { data: { session } } = await supabase.auth.getSession()
 * 
 * if (!session) {
 *   return NextResponse.redirect(new URL('/login', _request.url))
 * }
 * ```
 */
export function middleware(_request: NextRequest) {
  // TODO: Implement Supabase auth check
  // For now, allow all requests (implement when auth is ready)
  
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

