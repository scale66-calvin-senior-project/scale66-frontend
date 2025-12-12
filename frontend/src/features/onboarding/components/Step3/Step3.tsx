'use client';

import React, { useState } from 'react';
import type { OnboardingData } from '../../types';
import styles from './Step3.module.css';

export interface Step3Props {
  onNext: (data?: Partial<OnboardingData>) => void;
  onBack: () => void;
  onSkip: () => void;
  initialData?: OnboardingData;
  isSaving?: boolean;
}

const STYLE_OPTIONS = [
  'Modern & Minimal',
  'Bold & Vibrant',
  'Professional & Clean',
  'Playful & Fun',
  'Elegant & Sophisticated',
  'Rustic & Natural',
  'Tech & Futuristic',
  'Creative & Artistic',
];

export const Step3: React.FC<Step3Props> = ({ onNext, onBack, onSkip, initialData, isSaving = false }) => {
  const [selectedStyle, setSelectedStyle] = useState(initialData?.brandStyle || '');

  const handleNext = () => {
    onNext({ brandStyle: selectedStyle || undefined });
  };

  return (
    <div className={styles.step}>
      <h1 className={styles.title}>What&apos;s your brand style?</h1>
      <p className={styles.subtitle}>
        Choose the aesthetic that best represents your brand
      </p>

      <div className={styles.options}>
        {STYLE_OPTIONS.map((style) => (
          <button
            key={style}
            className={`${styles.option} ${selectedStyle === style ? styles.selected : ''}`}
            onClick={() => setSelectedStyle(style)}
          >
            {style}
          </button>
        ))}
      </div>

      <div className={styles.actions}>
        <button className={styles.backButton} onClick={onBack} disabled={isSaving}>
          Back
        </button>
        <button className={styles.skipButton} onClick={onSkip} disabled={isSaving}>
          Skip
        </button>
        <button className={styles.nextButton} onClick={handleNext} disabled={isSaving}>
          {isSaving ? 'Saving...' : 'Next'}
        </button>
      </div>
    </div>
  );
};

