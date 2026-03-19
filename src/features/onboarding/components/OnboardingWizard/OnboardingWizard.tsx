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
  const [isSaving, setIsSaving] = useState(false);

  const handleNext = async (stepData?: Partial<OnboardingData>) => {
    // Prevent multiple clicks while saving
    if (isSaving) return;

    // Merge new step data with existing data
    const updatedData = stepData 
      ? { ...onboardingData, ...stepData }
      : onboardingData;
    
    setOnboardingData(updatedData);
    setIsSaving(true);

    // Save to Supabase on each step - wait for it to complete before navigating
    try {
      console.log('💾 Saving onboarding data...', updatedData);
      
      // Ensure we have at least brandName for step 1
      if (currentStep === 1 && !updatedData.brandName?.trim()) {
        console.warn('⚠️ No brand name provided, skipping save');
        // Skip save for step 1 if no brand name
      } else {
        // Save with a timeout wrapper, but don't use Promise.race which cancels the operation
        const savePromise = onboardingService.saveBrandKit(updatedData);
        const timeoutId = setTimeout(() => {
          console.warn('⏱️ Save operation is taking longer than expected...');
        }, 8000); // Just log a warning, don't cancel
        
        try {
          await savePromise;
          clearTimeout(timeoutId);
          console.log('✅ Onboarding data saved successfully');
          
          // Small delay to ensure database consistency
          await new Promise(resolve => setTimeout(resolve, 200));
        } catch (saveError) {
          clearTimeout(timeoutId);
          throw saveError; // Re-throw to be caught by outer catch
        }
      }
    } catch (error) {
      console.error('❌ Error saving onboarding data:', error);
      
      // If session is invalid, redirect to login
      if (error instanceof Error && error.message.includes('session is invalid')) {
        setIsSaving(false);
        router.push('/login');
        return;
      }
      
      // Log the full error for debugging
      if (error instanceof Error) {
        console.error('Error details:', {
          message: error.message,
          stack: error.stack,
          data: updatedData,
          currentStep,
        });
      }
      
      // For step 1, if save fails, don't proceed - user needs to retry
      if (currentStep === 1) {
        console.error('❌ Step 1 save failed - user must retry');
        setIsSaving(false);
        // Show error to user (you might want to add a toast/alert here)
        alert('Failed to save brand name. Please try again.');
        return;
      }
      
      // For other steps, continue but log warning
      console.warn('⚠️ Save failed but continuing to next step');
    } finally {
      setIsSaving(false);
      console.log('🔄 isSaving set to false');
    }
    
    // Navigate to next step after save completes (only if save was successful or not step 1)
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

