'use client';

import React, { useState } from 'react';
import type { OnboardingData } from '../../types';
import styles from './Step1.module.css';

export interface Step1Props {
  onNext: (data?: Partial<OnboardingData>) => void;
  onSkip: () => void;
  initialData?: OnboardingData;
}

export const Step1: React.FC<Step1Props> = ({ onNext, onSkip, initialData }) => {
  const [brandName, setBrandName] = useState(initialData?.brandName || '');

  const handleNext = () => {
    onNext({ brandName: brandName.trim() || undefined });
  };

  return (
    <div className={styles.step}>
      <h1 className={styles.title}>What's your brand name?</h1>
      <p className={styles.subtitle}>
        This helps us personalize your content creation experience
      </p>

      <div className={styles.inputWrapper}>
        <input
          type="text"
          className={styles.input}
          placeholder="Enter your brand name"
          value={brandName}
          onChange={(e) => setBrandName(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && brandName.trim()) {
              handleNext();
            }
          }}
        />
      </div>

      <div className={styles.actions}>
        <button className={styles.skipButton} onClick={onSkip}>
          Skip
        </button>
        <button 
          className={styles.nextButton} 
          onClick={handleNext}
          disabled={!brandName.trim()}
        >
          Next
        </button>
      </div>
    </div>
  );
};

