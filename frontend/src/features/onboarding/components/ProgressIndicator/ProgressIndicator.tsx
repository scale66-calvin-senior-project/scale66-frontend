import React from 'react';
import styles from './ProgressIndicator.module.css';

export interface ProgressIndicatorProps {
  currentStep: number;
  totalSteps: number;
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  currentStep,
  totalSteps,
}) => {
  const progress = (currentStep / totalSteps) * 100;

  return (
    <div className={styles.container}>
      <div className={styles.progressBar}>
        <div 
          className={styles.progressFill} 
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className={styles.stepInfo}>
        Step {currentStep} of {totalSteps}
      </div>
    </div>
  );
};

