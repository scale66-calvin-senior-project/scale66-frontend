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
  // Initialize pain points from initialData
  const getInitialPainPoints = (): string[] => {
    if (!initialData?.customerPainPoints) return [''];
    if (Array.isArray(initialData.customerPainPoints)) {
      return initialData.customerPainPoints.length > 0 ? initialData.customerPainPoints : [''];
    }
    // If it's a string, split by newlines
    const points = initialData.customerPainPoints.split('\n').map(p => p.trim()).filter(p => p);
    return points.length > 0 ? points : [''];
  };

  const [painPoints, setPainPoints] = useState<string[]>(getInitialPainPoints());

  const handleAddInput = () => {
    setPainPoints([...painPoints, '']);
  };

  const handleRemoveInput = (index: number) => {
    if (painPoints.length > 1) {
      setPainPoints(painPoints.filter((_, i) => i !== index));
    }
  };

  const handleInputChange = (index: number, value: string) => {
    const updated = [...painPoints];
    updated[index] = value;
    setPainPoints(updated);
  };

  const handleNext = () => {
    // Filter out empty pain points and pass as array
    const filteredPainPoints = painPoints
      .map(p => p.trim())
      .filter(p => p.length > 0);
    
    onNext({ 
      customerPainPoints: filteredPainPoints.length > 0 ? filteredPainPoints : undefined 
    });
  };

  return (
    <div className={styles.step}>
      <h1 className={styles.title}>What are your customer&apos;s pain points?</h1>
      <p className={styles.subtitle}>
        Understanding your customers helps us create more targeted content
      </p>

      <div className={styles.inputsContainer}>
        {painPoints.map((painPoint, index) => (
          <div key={index} className={styles.inputGroup}>
            <div className={styles.inputWrapper}>
              <input
                type="text"
                className={styles.input}
                placeholder={`Pain point ${index + 1}...`}
                value={painPoint}
                onChange={(e) => handleInputChange(index, e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && painPoint.trim()) {
                    handleAddInput();
                  }
                }}
              />
              {painPoints.length > 1 && (
                <button
                  type="button"
                  className={styles.removeButton}
                  onClick={() => handleRemoveInput(index)}
                  aria-label="Remove pain point"
                >
                  ×
                </button>
              )}
            </div>
          </div>
        ))}
        
        <button
          type="button"
          className={styles.addButton}
          onClick={handleAddInput}
        >
          + Add Another Pain Point
        </button>
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
