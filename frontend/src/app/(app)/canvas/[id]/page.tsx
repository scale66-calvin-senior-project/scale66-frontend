'use client';

/**
 * Canvas Page (CORE FEATURE)
 * 
 * Dynamic route for campaign-specific canvas
 * Fully client-side - no generateStaticParams needed
 * 
 * Handles:
 * - AI chat interface for content generation
 * - Carousel generation via backend API
 * - Display generated carousel previews
 * - Handle variations generation
 * - Enable posting to social platforms
 */

import { CanvasPageClient } from './CanvasPageClient';
import { useParams } from 'next/navigation';

export default function CanvasPage() {
  const params = useParams();
  const campaignId = params.id as string;
  
  return <CanvasPageClient campaignId={campaignId} />;
}
