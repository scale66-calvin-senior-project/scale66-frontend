import { NextRequest, NextResponse } from 'next/server';
import { submitToWaitlist } from '@/features/landing/waitlist/services/waitlistService';

/**
 * POST /api/waitlist
 * Submit email to waitlist
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const result = await submitToWaitlist(body);
    return NextResponse.json(result);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

