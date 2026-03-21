'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useBrandKit } from '../../hooks';
import { BRAND_STYLE_OPTIONS } from '../../types';
import type { BrandKitFormData, BrandStyle } from '../../types';
import { SocialAccountsSection } from '../SocialAccountsSection';
import styles from './BrandKitPage.module.css';

/**
 * BrandKitPage Component
 * 
 * Displays and manages brand kit information with inline editing
 * and social media account connections
 */
export const BrandKitPage: React.FC = () => {
  const {
    brandKit,
    socialAccounts,
    isLoading,
    isSaving,
    error,
    saveBrandKit,
    connectSocialAccount,
    disconnectSocialAccount,
    clearError,
  } = useBrandKit();

  // Local form state
  const [formData, setFormData] = useState<BrandKitFormData>({
    brandName: '',
    brandNiche: '',
    brandStyle: undefined,
    customerPainPoints: '',
    productServiceDescription: '',
  });

  const [hasChanges, setHasChanges] = useState(false);

  // Sync form data with loaded brand kit
  useEffect(() => {
    if (brandKit) {
      setFormData({
        brandName: brandKit.brandName || '',
        brandNiche: brandKit.brandNiche || '',
        brandStyle: brandKit.brandStyle,
        customerPainPoints: brandKit.customerPainPoints || '',
        productServiceDescription: brandKit.productServiceDescription || '',
      });
    }
  }, [brandKit]);

  /**
   * Handle field change
   */
  const handleFieldChange = useCallback((
    field: keyof BrandKitFormData,
    value: string
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setHasChanges(true);
    clearError();
  }, [clearError]);

  /**
   * Handle style selection
   */
  const handleStyleChange = useCallback((style: BrandStyle) => {
    setFormData(prev => ({ ...prev, brandStyle: style }));
    setHasChanges(true);
    clearError();
  }, [clearError]);

  /**
   * Save changes
   */
  const handleSave = useCallback(async () => {
    if (!formData.productServiceDescription.trim()) {
      return;
    }

    const result = await saveBrandKit(formData);
    if (result) {
      setHasChanges(false);
    }
  }, [formData, saveBrandKit]);

  // Loading state
  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingState}>
          <div className={styles.spinner} />
          <p>Loading your brand kit...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <h1 className={styles.pageTitle}>Brand Kit</h1>
        {isSaving && (
          <div className={styles.savingIndicator}>
            <div className={styles.savingDot} />
            Saving...
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className={styles.errorBanner}>
          <span>{error}</span>
          <button className={styles.dismissButton} onClick={clearError}>
            Dismiss
          </button>
        </div>
      )}

      {/* Brand Section */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Brand</h2>
        
        <div className={styles.fieldRow}>
          <div className={styles.field}>
            <label className={styles.fieldLabel}>Name</label>
            <input
              type="text"
              className={styles.input}
              placeholder="Your brand name"
              value={formData.brandName}
              onChange={(e) => handleFieldChange('brandName', e.target.value)}
            />
          </div>
          
          <div className={styles.field}>
            <label className={styles.fieldLabel}>Style</label>
            <select
              className={styles.select}
              value={formData.brandStyle || ''}
              onChange={(e) => handleStyleChange(e.target.value as BrandStyle)}
            >
              <option value="">Select a style</option>
              {BRAND_STYLE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className={styles.field}>
          <label className={styles.fieldLabel}>Describe your niche</label>
          <input
            type="text"
            className={styles.input}
            placeholder="e.g., I sell insurance, We create handmade jewelry"
            value={formData.brandNiche}
            onChange={(e) => handleFieldChange('brandNiche', e.target.value)}
          />
        </div>
      </section>

      {/* Audience Section */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Audience</h2>
        
        <div className={styles.field}>
          <label className={styles.fieldLabel}>Your audience's pain points</label>
          <textarea
            className={styles.textarea}
            placeholder="What problems does your audience face? What do they want to achieve?"
            value={formData.customerPainPoints}
            onChange={(e) => handleFieldChange('customerPainPoints', e.target.value)}
            rows={3}
          />
        </div>
      </section>

      {/* Product/Service Section */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Product/Service</h2>
        
        <div className={styles.field}>
          <label className={styles.fieldLabel}>
            Product/Service Description
            <span className={styles.required}>*</span>
          </label>
          <textarea
            className={styles.textarea}
            placeholder="Describe what you offer to your customers..."
            value={formData.productServiceDescription}
            onChange={(e) => handleFieldChange('productServiceDescription', e.target.value)}
            rows={4}
            required
          />
          {!formData.productServiceDescription.trim() && (
            <span className={styles.fieldHint}>This field is required</span>
          )}
        </div>
      </section>

      {/* Social Accounts Section */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Connected Accounts</h2>
        <SocialAccountsSection
          accounts={socialAccounts}
          onConnect={connectSocialAccount}
          onDisconnect={disconnectSocialAccount}
        />
      </section>

      {/* Actions */}
      <div className={styles.actions}>
        {hasChanges && (
          <button
            className={styles.saveButton}
            onClick={handleSave}
            disabled={isSaving || !formData.productServiceDescription.trim()}
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        )}
      </div>
    </div>
  );
};

export default BrandKitPage;

