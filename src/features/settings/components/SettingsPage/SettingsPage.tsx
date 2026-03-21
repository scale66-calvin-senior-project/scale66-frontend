'use client';

import React, { useState, useCallback } from 'react';
import { useSettings } from '../../hooks';
import { SUBSCRIPTION_TIERS } from '../../types';
import styles from './SettingsPage.module.css';

/**
 * SettingsPage Component
 * 
 * Displays user profile settings and subscription management
 * with inline editing and Stripe integration
 */
export const SettingsPage: React.FC = () => {
  const {
    profile,
    subscription,
    billingHistory,
    isLoading,
    isSaving,
    error,
    updateProfile,
    changePassword,
    openCustomerPortal,
    cancelSubscription,
    resumeSubscription,
    deleteAccount,
    signOut,
    clearError,
  } = useSettings();

  // Profile form state
  const [email, setEmail] = useState('');
  const [isEditingEmail, setIsEditingEmail] = useState(false);

  // Password form state
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  // Modal states
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showSignOutModal, setShowSignOutModal] = useState(false);

  // Initialize email when profile loads
  React.useEffect(() => {
    if (profile?.email) {
      setEmail(profile.email);
    }
  }, [profile?.email]);

  /**
   * Handle email update
   */
  const handleEmailSave = useCallback(async () => {
    if (!email.trim() || email === profile?.email) {
      setIsEditingEmail(false);
      return;
    }

    const success = await updateProfile({ email: email.trim() });
    if (success) {
      setIsEditingEmail(false);
    }
  }, [email, profile?.email, updateProfile]);

  /**
   * Handle password change
   */
  const handlePasswordChange = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess(false);

    if (newPassword !== confirmPassword) {
      setPasswordError('Passwords do not match');
      return;
    }

    if (newPassword.length < 8) {
      setPasswordError('Password must be at least 8 characters');
      return;
    }

    const success = await changePassword(currentPassword, newPassword);
    if (success) {
      setPasswordSuccess(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setTimeout(() => {
        setShowPasswordForm(false);
        setPasswordSuccess(false);
      }, 2000);
    }
  }, [currentPassword, newPassword, confirmPassword, changePassword]);

  /**
   * Handle subscription cancel
   */
  const handleCancelSubscription = useCallback(async () => {
    const success = await cancelSubscription();
    if (success) {
      setShowCancelModal(false);
    }
  }, [cancelSubscription]);

  /**
   * Handle account deletion
   */
  const handleDeleteAccount = useCallback(async () => {
    const success = await deleteAccount();
    if (success) {
      // Redirect to home after deletion
      window.location.href = '/';
    }
  }, [deleteAccount]);

  /**
   * Get tier display info
   */
  const getCurrentTierInfo = () => {
    return SUBSCRIPTION_TIERS.find(t => t.tier === (subscription?.tier || profile?.subscriptionTier || 'free'));
  };

  /**
   * Format date for display
   */
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  /**
   * Format currency
   */
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingState}>
          <div className={styles.spinner} />
          <p>Loading your settings...</p>
        </div>
      </div>
    );
  }

  const tierInfo = getCurrentTierInfo();

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <h1 className={styles.pageTitle}>Settings</h1>
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

      {/* Profile Section */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Profile</h2>

        <div className={styles.profileCard}>
          {/* Email Field */}
          <div className={styles.fieldGroup}>
            <label className={styles.fieldLabel}>Email Address</label>
            {isEditingEmail ? (
              <div className={styles.editRow}>
                <input
                  type="email"
                  className={styles.input}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoFocus
                />
                <button
                  className={styles.saveButton}
                  onClick={handleEmailSave}
                  disabled={isSaving}
                >
                  Save
                </button>
                <button
                  className={styles.cancelButton}
                  onClick={() => {
                    setEmail(profile?.email || '');
                    setIsEditingEmail(false);
                  }}
                >
                  Cancel
                </button>
              </div>
            ) : (
              <div className={styles.valueRow}>
                <span className={styles.fieldValue}>{profile?.email || 'Not set'}</span>
                <button
                  className={styles.editButton}
                  onClick={() => setIsEditingEmail(true)}
                >
                  Edit
                </button>
              </div>
            )}
          </div>

          {/* Password Field */}
          <div className={styles.fieldGroup}>
            <label className={styles.fieldLabel}>Password</label>
            {showPasswordForm ? (
              <form className={styles.passwordForm} onSubmit={handlePasswordChange}>
                <input
                  type="password"
                  className={styles.input}
                  placeholder="Current password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  required
                />
                <input
                  type="password"
                  className={styles.input}
                  placeholder="New password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={8}
                />
                <input
                  type="password"
                  className={styles.input}
                  placeholder="Confirm new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
                {passwordError && (
                  <span className={styles.fieldError}>{passwordError}</span>
                )}
                {passwordSuccess && (
                  <span className={styles.fieldSuccess}>Password changed successfully!</span>
                )}
                <div className={styles.passwordActions}>
                  <button
                    type="submit"
                    className={styles.saveButton}
                    disabled={isSaving}
                  >
                    {isSaving ? 'Updating...' : 'Update Password'}
                  </button>
                  <button
                    type="button"
                    className={styles.cancelButton}
                    onClick={() => {
                      setShowPasswordForm(false);
                      setCurrentPassword('');
                      setNewPassword('');
                      setConfirmPassword('');
                      setPasswordError('');
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <div className={styles.valueRow}>
                <span className={styles.fieldValue}>********</span>
                <button
                  className={styles.editButton}
                  onClick={() => setShowPasswordForm(true)}
                >
                  Change
                </button>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Account Section */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Account</h2>

        <div className={styles.accountCard}>
          <div className={styles.accountInfo}>
            <h4>Sign Out</h4>
            <p>Sign out of your account on this device.</p>
          </div>
          <button
            className={styles.signOutButton}
            onClick={() => setShowSignOutModal(true)}
          >
            Sign Out
          </button>
        </div>
      </section>

      {/* Subscription Section */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Subscription</h2>

        <div className={styles.subscriptionCard}>
          <div className={styles.planInfo}>
            <div className={styles.planHeader}>
              <span className={styles.planName}>{tierInfo?.name || 'Free'}</span>
              <span className={styles.planBadge}>
                {subscription?.status === 'active' ? 'Active' : 
                 subscription?.cancelAtPeriodEnd ? 'Canceling' :
                 subscription?.status || 'Active'}
              </span>
            </div>
            <div className={styles.planPrice}>
              <span className={styles.priceAmount}>
                {formatCurrency(tierInfo?.price || 0)}
              </span>
              <span className={styles.priceInterval}>/{tierInfo?.interval || 'month'}</span>
            </div>
            {subscription?.currentPeriodEnd && (
              <p className={styles.planRenewal}>
                {subscription.cancelAtPeriodEnd
                  ? `Access until ${formatDate(subscription.currentPeriodEnd)}`
                  : `Renews on ${formatDate(subscription.currentPeriodEnd)}`}
              </p>
            )}
          </div>

          <div className={styles.planFeatures}>
            <h4 className={styles.featuresTitle}>Plan includes:</h4>
            <ul className={styles.featuresList}>
              {tierInfo?.features.map((feature, index) => (
                <li key={index} className={styles.featureItem}>
                  <span className={styles.checkIcon}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </span>
                  {feature}
                </li>
              ))}
            </ul>
          </div>

          <div className={styles.subscriptionActions}>
            <button
              className={styles.portalButton}
              onClick={openCustomerPortal}
            >
              Manage Payment Method
            </button>
            {subscription?.cancelAtPeriodEnd ? (
              <button
                className={styles.resumeButton}
                onClick={resumeSubscription}
                disabled={isSaving}
              >
                Resume Subscription
              </button>
            ) : subscription?.tier !== 'free' && (
              <button
                className={styles.cancelSubButton}
                onClick={() => setShowCancelModal(true)}
              >
                Cancel Subscription
              </button>
            )}
          </div>
        </div>
      </section>

      {/* Billing History Section */}
      {billingHistory.length > 0 && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Billing History</h2>

          <div className={styles.billingTable}>
            <div className={styles.tableHeader}>
              <span>Date</span>
              <span>Description</span>
              <span>Amount</span>
              <span>Status</span>
            </div>
            {billingHistory.map((transaction) => (
              <div key={transaction.id} className={styles.tableRow}>
                <span>{formatDate(transaction.createdAt)}</span>
                <span className={styles.tierLabel}>
                  {SUBSCRIPTION_TIERS.find(t => t.tier === transaction.subscriptionTier)?.name || transaction.subscriptionTier} Plan
                </span>
                <span>{formatCurrency(transaction.amount)}</span>
                <span className={`${styles.statusBadge} ${styles[transaction.status]}`}>
                  {transaction.status}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Danger Zone */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitleDanger}>Danger Zone</h2>

        <div className={styles.dangerCard}>
          <div className={styles.dangerInfo}>
            <h4>Delete Account</h4>
            <p>Permanently delete your account and all associated data. This action cannot be undone.</p>
          </div>
          <button
            className={styles.deleteAccountButton}
            onClick={() => setShowDeleteModal(true)}
          >
            Delete Account
          </button>
        </div>
      </section>

      {/* Cancel Subscription Modal */}
      {showCancelModal && (
        <div className={styles.modalOverlay} onClick={() => setShowCancelModal(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h3 className={styles.modalTitle}>Cancel Subscription?</h3>
            <p className={styles.modalText}>
              Your subscription will remain active until the end of your current billing period.
              You can resume at any time before then.
            </p>
            <div className={styles.modalActions}>
              <button
                className={styles.modalCancelButton}
                onClick={() => setShowCancelModal(false)}
              >
                Keep Subscription
              </button>
              <button
                className={styles.modalConfirmButton}
                onClick={handleCancelSubscription}
                disabled={isSaving}
              >
                {isSaving ? 'Canceling...' : 'Cancel Subscription'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Account Modal */}
      {showDeleteModal && (
        <div className={styles.modalOverlay} onClick={() => setShowDeleteModal(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h3 className={styles.modalTitle}>Delete Account?</h3>
            <p className={styles.modalText}>
              This will permanently delete your account, all campaigns, carousels, and data.
              This action cannot be undone.
            </p>
            <div className={styles.modalActions}>
              <button
                className={styles.modalCancelButton}
                onClick={() => setShowDeleteModal(false)}
              >
                Cancel
              </button>
              <button
                className={styles.modalDeleteButton}
                onClick={handleDeleteAccount}
                disabled={isSaving}
              >
                {isSaving ? 'Deleting...' : 'Delete Account'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Sign Out Modal */}
      {showSignOutModal && (
        <div className={styles.modalOverlay} onClick={() => setShowSignOutModal(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h3 className={styles.modalTitle}>Sign Out?</h3>
            <p className={styles.modalText}>
              You will be signed out of your account and redirected to the login page.
            </p>
            <div className={styles.modalActions}>
              <button
                className={styles.modalCancelButton}
                onClick={() => setShowSignOutModal(false)}
              >
                Cancel
              </button>
              <button
                className={styles.signOutConfirmButton}
                onClick={signOut}
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;

