'use client';

/**
 * Canvas Page (CORE FEATURE)
 * 
 * Single page that handles all canvas routes via query parameter
 * This avoids the need for generateStaticParams with static export
 * 
 * Handles:
 * - AI chat interface for content generation
 * - Carousel generation via backend API
 * - Display generated carousel previews
 * - Handle variations generation
 * - Enable posting to social platforms
 */

import { CanvasPageClient } from './[id]/CanvasPageClient';
import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';

function CanvasPageContent() {
  const searchParams = useSearchParams();
  // Get campaign ID from query parameter instead of path
  const campaignId = searchParams.get('id') || searchParams.get('campaignId') || '';
  
  return <CanvasPageClient campaignId={campaignId} />;
}

export default function CanvasPage() {
  return (
    <Suspense fallback={<div style={{ padding: '2rem', textAlign: 'center' }}>Loading...</div>}>
      <CanvasPageContent />
    </Suspense>
  );
}




