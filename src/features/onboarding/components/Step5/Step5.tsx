'use client';

import React, { useState } from 'react';
import type { OnboardingData } from '../../types';
import styles from './Step5.module.css';

export interface Step5Props {
  onNext: (data?: Partial<OnboardingData>) => void;
  onBack: () => void;
  onSkip: () => void;
  initialData?: OnboardingData;
  isSaving?: boolean;
}

export const Step5: React.FC<Step5Props> = ({ onNext, onBack, initialData, isSaving = false }) => {
  const [productService, setProductService] = useState(initialData?.productService || '');

  const handleNext = () => {
    if (!productService.trim()) {
      return;
    }
    onNext({ productService: productService.trim() });
  };

  return (
    <div className={styles.step}>
      <h1 className={styles.title}>What product or service do you offer?</h1>
      <p className={styles.subtitle}>
        Tell us about what you&apos;re selling or providing to your customers
      </p>

      <div className={styles.inputWrapper}>
        <textarea
          className={styles.textarea}
          placeholder="Describe your product or service..."
          value={productService}
          onChange={(e) => setProductService(e.target.value)}
          rows={6}
        />
      </div>

      <div className={styles.actions}>
        <button className={styles.backButton} onClick={onBack} disabled={isSaving}>
          Back
        </button>
        <button 
          className={styles.nextButton} 
          onClick={handleNext}
          disabled={!productService.trim() || isSaving}
        >
          {isSaving ? 'Saving...' : 'Next'}
        </button>
      </div>
    </div>
  );
};

