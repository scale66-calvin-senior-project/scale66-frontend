'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { onboardingService } from '../../services';
import { ProgressIndicator } from '../ProgressIndicator';
import { Step1 } from '../Step1';
import { Step2 } from '../Step2';
import { Step3 } from '../Step3';
import { Step4 } from '../Step4';
import { Step5 } from '../Step5';
import { Step6_5 } from '../Step6_5';
import { PricingCards } from '@/features/payment';
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
  // Load initial data from localStorage if available
  const [onboardingData, setOnboardingData] = useState<OnboardingData>(() => {
    if (typeof window !== 'undefined') {
      return onboardingService.loadFromLocalStorage() as OnboardingData;
    }
    return {};
  });
  const [isSaving, setIsSaving] = useState(false);

  const handleNext = async (stepData?: Partial<OnboardingData>) => {
    // Prevent multiple clicks while saving
    if (isSaving) return;

    // Merge new step data with existing data
    const updatedData = stepData 
      ? { ...onboardingData, ...stepData }
      : onboardingData;
    
    setOnboardingData(updatedData);
    
    // Save to localStorage immediately (synchronous, no API call)
    onboardingService.saveToLocalStorage(updatedData);
    console.log('💾 Saved to localStorage:', updatedData);
    
    // Navigate to next step immediately (no waiting for API)
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

  const handleComplete = async (data?: OnboardingData) => {
    // Use provided data or fall back to state
    const dataToSave = data || onboardingData;
    
    // Save all onboarding data to backend API and mark as complete
    setIsSaving(true);
    
    try {
      console.log('🚀 Completing onboarding, saving all data to backend...', dataToSave);
      
      // Save all data to backend and mark as complete in one call
      await onboardingService.saveAndCompleteOnboarding(dataToSave);
      
      console.log('✅ Onboarding completed successfully');
      
      onComplete?.(dataToSave);
      router.push('/dashboard');
    } catch (error) {
      console.error('❌ Error completing onboarding:', error);
      
      // Show error to user but don't block navigation
      alert('There was an error saving your onboarding data. Your data has been saved locally. Please try again or contact support.');
      
      // Still navigate to dashboard - data is in localStorage and can be retried
      onComplete?.(dataToSave);
      router.push('/dashboard');
    } finally {
      setIsSaving(false);
    }
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
        return <Step1 onNext={handleNext} onSkip={handleSkip} initialData={onboardingData} isSaving={isSaving} />;
      case 2:
        return <Step2 onNext={handleNext} onBack={handleBack} onSkip={handleSkip} initialData={onboardingData} isSaving={isSaving} />;
      case 3:
        return <Step3 onNext={handleNext} onBack={handleBack} onSkip={handleSkip} initialData={onboardingData} isSaving={isSaving} />;
      case 4:
        return <Step4 onNext={handleNext} onBack={handleBack} onSkip={handleSkip} initialData={onboardingData} isSaving={isSaving} />;
      case 5:
        return <Step5 onNext={handleNext} onBack={handleBack} onSkip={handleSkip} initialData={onboardingData} isSaving={isSaving} />;
      // Step6 (social media handles) is skipped - not shown in flow
      case 6:
        return <Step6_5 onNext={handleNext} onBack={handleBack} initialData={onboardingData} isSaving={isSaving} />;
      case 7:
        return (
          <PricingCards
            onBack={handleBack}
            onComplete={(planId) => {
              // Save selected plan to onboarding data and localStorage
              // Don't save to database yet - that happens on payment success page
              const updatedData = {
                ...onboardingData,
                paywallSelection: { plan: planId as 'agency' | 'growth' | 'starter' },
              };
              setOnboardingData(updatedData);
              // Save to localStorage - payment success page will save to database
              onboardingService.saveToLocalStorage(updatedData);
              // Note: handleComplete is NOT called here because user is redirected to Stripe
              // The payment success page will handle saving brand kit and completing onboarding
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

