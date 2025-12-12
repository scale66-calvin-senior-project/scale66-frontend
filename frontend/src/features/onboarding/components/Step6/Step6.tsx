'use client';

import React, { useState } from 'react';
import type { OnboardingData } from '../../types';
import styles from './Step6.module.css';

export interface Step6Props {
  onNext: (data?: Partial<OnboardingData>) => void;
  onBack: () => void;
  onComplete: () => void;
  initialData?: OnboardingData;
}

export const Step6: React.FC<Step6Props> = ({ onNext, onBack, onComplete, initialData }) => {
  const [socialLinks, setSocialLinks] = useState({
    instagram: initialData?.socialMediaLinks?.instagram || '',
    tiktok: initialData?.socialMediaLinks?.tiktok || '',
  });

  const handleNext = () => {
    const hasAnyLink = Object.values(socialLinks).some(link => link.trim());
    if (hasAnyLink) {
      onNext({ 
        socialMediaLinks: {
          instagram: socialLinks.instagram.trim() || undefined,
          tiktok: socialLinks.tiktok.trim() || undefined,
        }
      });
    } else {
      onNext();
    }
  };

  const handleLinkChange = (platform: keyof typeof socialLinks, value: string) => {
    setSocialLinks((prev) => ({ ...prev, [platform]: value }));
  };

  return (
    <div className={styles.step}>
      <h1 className={styles.title}>Connect your social media</h1>
      <p className={styles.subtitle}>
        Link your accounts to enable automatic posting (optional)
      </p>

      <div className={styles.linksContainer}>
        <div className={styles.linkInput}>
          <label className={styles.label}>Instagram</label>
          <input
            type="text"
            className={styles.input}
            placeholder="@yourusername or URL"
            value={socialLinks.instagram}
            onChange={(e) => handleLinkChange('instagram', e.target.value)}
          />
        </div>

        <div className={styles.linkInput}>
          <label className={styles.label}>TikTok</label>
          <input
            type="text"
            className={styles.input}
            placeholder="@yourusername or URL"
            value={socialLinks.tiktok}
            onChange={(e) => handleLinkChange('tiktok', e.target.value)}
          />
        </div>
      </div>

      <div className={styles.actions}>
        <button className={styles.backButton} onClick={onBack}>
          Back
        </button>
        <button className={styles.nextButton} onClick={handleNext}>
          Next
        </button>
      </div>
    </div>
  );
};

