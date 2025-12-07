'use client';

import React, { useState } from 'react';
import { authService } from '../../services';
import type { SignupData } from '../../types';
import styles from './SignupForm.module.css';

export interface SignupFormProps {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

export const SignupForm: React.FC<SignupFormProps> = ({ onSuccess, onError }) => {
  const [formData, setFormData] = useState<SignupData>({
    email: '',
    password: '',
    name: '',
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (formData.password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setIsLoading(true);

    try {
      await authService.signup(formData);
      onSuccess?.();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred during signup';
      setError(errorMessage);
      onError?.(err as Error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: keyof SignupData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData((prev) => ({ ...prev, [field]: e.target.value }));
  };

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      {error && <div className={styles.errorMessage}>{error}</div>}

      <div className={styles.inputGroup}>
        <label htmlFor="name" className={styles.label}>
          Name (Optional)
        </label>
        <input
          id="name"
          type="text"
          className={styles.input}
          placeholder="Enter your name"
          value={formData.name}
          onChange={handleChange('name')}
          disabled={isLoading}
        />
      </div>

      <div className={styles.inputGroup}>
        <label htmlFor="email" className={styles.label}>
          Email
        </label>
        <input
          id="email"
          type="email"
          className={styles.input}
          placeholder="Enter your email"
          value={formData.email}
          onChange={handleChange('email')}
          required
          disabled={isLoading}
        />
      </div>

      <div className={styles.inputGroup}>
        <label htmlFor="password" className={styles.label}>
          Password
        </label>
        <input
          id="password"
          type="password"
          className={styles.input}
          placeholder="Create a password (min. 6 characters)"
          value={formData.password}
          onChange={handleChange('password')}
          required
          disabled={isLoading}
          minLength={6}
        />
      </div>

      <div className={styles.inputGroup}>
        <label htmlFor="confirmPassword" className={styles.label}>
          Confirm Password
        </label>
        <input
          id="confirmPassword"
          type="password"
          className={styles.input}
          placeholder="Confirm your password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          disabled={isLoading}
        />
      </div>

      <button
        type="submit"
        className={styles.submitButton}
        disabled={isLoading}
      >
        {isLoading ? 'Creating account...' : 'Create Account'}
      </button>
    </form>
  );
};

export default SignupForm;
