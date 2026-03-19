/**
 * Welcome Page
 *
 * Multi-step wizard for new user setup (8 steps)
 * Handles onboarding flow and paywall redirects
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

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { OnboardingWizard } from '@/features/onboarding';

function WelcomePageContent() {
	const router = useRouter();
	const searchParams = useSearchParams();
	const [isVerifying, setIsVerifying] = useState(true);
	const [isAuthenticated, setIsAuthenticated] = useState(false);
	const [initialStep, setInitialStep] = useState<number | undefined>(undefined);

	useEffect(() => {
		// Check if user has a valid session
		// Email verification should have already happened in the confirm-email page
		const checkSession = async () => {
			const { data: { session }, error } = await supabase.auth.getSession();
			
			if (session && !error) {
				// Check if user has completed onboarding and should be redirected
				const { data: { user: authUser } } = await supabase.auth.getUser();
				if (authUser) {
					const { data: userData } = await supabase
						.from('users')
						.select('id, email, subscription_tier, onboarding_completed')
						.eq('id', authUser.id)
						.single();
					
					if (userData) {
						// If onboarding completed and paid, redirect to dashboard
						if (userData.onboarding_completed && 
							(userData.subscription_tier === 'starter' || userData.subscription_tier === 'growth' || userData.subscription_tier === 'agency')) {
							router.push('/dashboard');
							return;
						}
						
						// If onboarding completed but not paid, check for step parameter
						if (userData.onboarding_completed && userData.subscription_tier === 'free') {
							const stepParam = searchParams.get('step');
							if (stepParam === '7') {
								// User is being sent to paywall
								setInitialStep(7);
							} else {
								// Redirect to paywall
								router.push('/welcome?step=7');
								return;
							}
						}
						
						// Check for step parameter in URL (for paywall redirect)
						const stepParam = searchParams.get('step');
						if (stepParam) {
							const step = parseInt(stepParam, 10);
							if (step >= 1 && step <= 7) {
								setInitialStep(step);
							}
						}
					}
				}
				
				setIsAuthenticated(true);
				setIsVerifying(false);
			} else {
				// No session - redirect to login
				router.push('/login');
			}
		};

		checkSession();
	}, [router, searchParams]);

	if (isVerifying) {
		return (
			<div style={{ 
				display: 'flex', 
				justifyContent: 'center', 
				alignItems: 'center', 
				minHeight: '100vh' 
			}}>
				<p>Verifying your email...</p>
			</div>
		);
	}

	if (!isAuthenticated) {
		return null; // Will redirect
	}

	return <OnboardingWizard initialStep={initialStep} />;
}

export default function WelcomePage() {
	return (
		<Suspense fallback={
			<div style={{ 
				display: 'flex', 
				justifyContent: 'center', 
				alignItems: 'center', 
				minHeight: '100vh' 
			}}>
				<p>Loading...</p>
			</div>
		}>
			<WelcomePageContent />
		</Suspense>
	);
}

