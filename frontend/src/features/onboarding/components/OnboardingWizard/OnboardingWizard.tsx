'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { ProgressIndicator } from '../ProgressIndicator';
import { Step1 } from '../Step1';
import { Step2 } from '../Step2';
import { Step3 } from '../Step3';
import { Step4 } from '../Step4';
import { Step5 } from '../Step5';
import { Step6 } from '../Step6';
import { Step6_5 } from '../Step6_5';
import { PricingCards } from '@/features/payment';
import { onboardingService } from '../../services';
import type { OnboardingData } from '../../types';
import styles from './OnboardingWizard.module.css';

const TOTAL_STEPS = 7;

export interface OnboardingWizardProps {
  onComplete?: (data: OnboardingData) => void;
  initialStep?: number; // Optional initial step (1-7)
}

export const OnboardingWizard: React.FC<OnboardingWizardProps> = ({ onComplete, initialStep }) => {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(initialStep || 1);
  const [onboardingData, setOnboardingData] = useState<OnboardingData>({});

  const handleNext = async (stepData?: Partial<OnboardingData>) => {
    // Merge new step data with existing data
    const updatedData = stepData 
      ? { ...onboardingData, ...stepData }
      : onboardingData;
    
    setOnboardingData(updatedData);

    // Save to Supabase on each step
    try {
      await onboardingService.saveBrandKit(updatedData);
    } catch (error) {
      console.error('Error saving onboarding data:', error);
      // If session is invalid, redirect to login
      if (error instanceof Error && error.message.includes('session is invalid')) {
        router.push('/login');
        return;
      }
      // Continue even if save fails - don't block user progress
    }

    // Skip Step6 (social media handles) - go directly from Step5 to Step6_5
    let nextStep = currentStep + 1;
    if (currentStep === 5) {
      // Skip Step6, go to Step6_5 (which is now step 6)
      nextStep = 6;
    }

    if (nextStep <= TOTAL_STEPS) {
      setCurrentStep(nextStep);
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      // Skip Step6 (social media handles) when going back
      let prevStep = currentStep - 1;
      if (currentStep === 6) {
        // If on Step6_5, go back to Step5 (skip Step6)
        prevStep = 5;
      }
      setCurrentStep(prevStep);
    }
  };

  const handleComplete = async () => {
    // Mark onboarding as completed in the database
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        await supabase
          .from('users')
          .update({ onboarding_completed: true })
          .eq('id', user.id);
      }
    } catch (error) {
      console.error('Error marking onboarding as completed:', error);
      // Continue anyway - don't block user
    }
    
    onComplete?.(onboardingData);
    router.push('/dashboard');
  };

  const handleSkip = () => {
    // Skip Step6 (social media handles) - go directly from Step5 to Step6_5
    let nextStep = currentStep + 1;
    if (currentStep === 5) {
      // Skip Step6, go to Step6_5 (which is now step 6)
      nextStep = 6;
    }

    if (nextStep <= TOTAL_STEPS) {
      setCurrentStep(nextStep);
    } else {
      handleComplete();
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <Step1 onNext={handleNext} onSkip={handleSkip} initialData={onboardingData} />;
      case 2:
        return <Step2 onNext={handleNext} onBack={handleBack} onSkip={handleSkip} initialData={onboardingData} />;
      case 3:
        return <Step3 onNext={handleNext} onBack={handleBack} onSkip={handleSkip} initialData={onboardingData} />;
      case 4:
        return <Step4 onNext={handleNext} onBack={handleBack} onSkip={handleSkip} initialData={onboardingData} />;
      case 5:
        return <Step5 onNext={handleNext} onBack={handleBack} onSkip={handleSkip} initialData={onboardingData} />;
      // Step6 (social media handles) is skipped - not shown in flow
      case 6:
        return <Step6_5 onNext={handleNext} onBack={handleBack} initialData={onboardingData} />;
      case 7:
        return (
          <PricingCards
            onBack={handleBack}
            onComplete={(planId) => {
              // Save selected plan to onboarding data
              setOnboardingData((prev) => ({
                ...prev,
                paywallSelection: { plan: planId as 'agency' | 'growth' | 'starter' },
              }));
              handleComplete();
            }}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className={`${styles.wizard} ${currentStep === 7 ? styles.step7Active : ''}`}>
      {currentStep !== 7 && <ProgressIndicator currentStep={currentStep} totalSteps={TOTAL_STEPS} />}
      <div className={styles.content}>
        {renderStep()}
      </div>
    </div>
  );
};

