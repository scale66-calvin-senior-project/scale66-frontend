/**
 * Welcome Page
 *
 * Multi-step wizard for new user setup (8 steps)
 * Only shown to new signups, not returning users
 *
 * Steps:
 * - Step 1: Brand Name (optional)
 * - Step 2: Brand Niche (optional)
 * - Step 3: Brand Style (optional)
 * - Step 4: Customer Pain Points (optional)
 * - Step 5: Product/Service (REQUIRED)
 * - Step 6: Social Media Links (optional)
 * - Step 6.5: Marketing Insights Synopsis
 * - Step 7: Pricing/Plan Selection
 * - After completion: Redirect to Dashboard
 */
'use client';

import { OnboardingWizard } from '@/features/onboarding';

export default function WelcomePage() {
	return <OnboardingWizard />;
}

