'use client';

import React, { useState } from 'react';
import type { OnboardingData } from '../../types';
import styles from './Step4.module.css';

export interface Step4Props {
  onNext: (data?: Partial<OnboardingData>) => void;
  onBack: () => void;
  onSkip: () => void;
  initialData?: OnboardingData;
}

export const Step4: React.FC<Step4Props> = ({ onNext, onBack, onSkip, initialData }) => {
  const [painPoints, setPainPoints] = useState(initialData?.customerPainPoints || '');

  const handleNext = () => {
    onNext({ customerPainPoints: painPoints.trim() || undefined });
  };

  return (
    <div className={styles.step}>
      <h1 className={styles.title}>What are your customer's pain points?</h1>
      <p className={styles.subtitle}>
        Understanding your customers helps us create more targeted content
      </p>

      <div className={styles.inputWrapper}>
        <textarea
          className={styles.textarea}
          placeholder="Describe the main challenges your customers face..."
          value={painPoints}
          onChange={(e) => setPainPoints(e.target.value)}
          rows={6}
        />
      </div>

      <div className={styles.actions}>
        <button className={styles.backButton} onClick={onBack}>
          Back
        </button>
        <button className={styles.skipButton} onClick={onSkip}>
          Skip
        </button>
        <button className={styles.nextButton} onClick={handleNext}>
          Next
        </button>
      </div>
    </div>
  );
};

