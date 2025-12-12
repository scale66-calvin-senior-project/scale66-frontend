'use client';

import React, { useState } from 'react';
import type { OnboardingData } from '../../types';
import styles from './Step2.module.css';

export interface Step2Props {
  onNext: (data?: Partial<OnboardingData>) => void;
  onBack: () => void;
  onSkip: () => void;
  initialData?: OnboardingData;
}

const NICHE_OPTIONS = [
  'E-commerce',
  'SaaS',
  'Fitness & Wellness',
  'Food & Beverage',
  'Fashion & Beauty',
  'Technology',
  'Education',
  'Healthcare',
  'Real Estate',
  'Finance',
  'Other',
];

export const Step2: React.FC<Step2Props> = ({ onNext, onBack, onSkip, initialData }) => {
  const [selectedNiche, setSelectedNiche] = useState(initialData?.brandNiche || '');

  const handleNext = () => {
    onNext({ brandNiche: selectedNiche || undefined });
  };

  return (
    <div className={styles.step}>
      <h1 className={styles.title}>What&apos;s your brand niche?</h1>
      <p className={styles.subtitle}>
        Help us understand your industry to create more relevant content
      </p>

      <div className={styles.options}>
        {NICHE_OPTIONS.map((niche) => (
          <button
            key={niche}
            className={`${styles.option} ${selectedNiche === niche ? styles.selected : ''}`}
            onClick={() => setSelectedNiche(niche)}
          >
            {niche}
          </button>
        ))}
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

