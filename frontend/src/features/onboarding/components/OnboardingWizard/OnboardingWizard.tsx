'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ProgressIndicator } from '../ProgressIndicator';
import { Step1 } from '../Step1';
import { Step2 } from '../Step2';
import { Step3 } from '../Step3';
import { Step4 } from '../Step4';
import { Step5 } from '../Step5';
import { Step6 } from '../Step6';
import { Step7 } from '../Step7';
import type { OnboardingData } from '../../types';
import styles from './OnboardingWizard.module.css';

const TOTAL_STEPS = 7;

export interface OnboardingWizardProps {
  onComplete?: (data: OnboardingData) => void;
}

export const OnboardingWizard: React.FC<OnboardingWizardProps> = ({ onComplete }) => {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [onboardingData, setOnboardingData] = useState<OnboardingData>({});

  const handleNext = (stepData?: Partial<OnboardingData>) => {
    if (stepData) {
      setOnboardingData((prev) => ({ ...prev, ...stepData }));
    }

    if (currentStep < TOTAL_STEPS) {
      setCurrentStep((prev) => prev + 1);
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  const handleComplete = () => {
    onComplete?.(onboardingData);
    router.push('/dashboard');
  };

  const handleSkip = () => {
    if (currentStep < TOTAL_STEPS) {
      setCurrentStep((prev) => prev + 1);
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
      case 6:
        return <Step6 onNext={handleNext} onBack={handleBack} onSkip={handleSkip} initialData={onboardingData} />;
      case 7:
        return <Step7 onBack={handleBack} onComplete={handleComplete} />;
      default:
        return null;
    }
  };

  return (
    <div className={styles.wizard}>
      <ProgressIndicator currentStep={currentStep} totalSteps={TOTAL_STEPS} />
      <div className={styles.content}>
        {renderStep()}
      </div>
    </div>
  );
};

