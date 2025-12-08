'use client';

import { useRouter } from 'next/navigation';
import { SignupForm } from '@/features/auth';
import styles from '../auth-page.module.css';

/**
 * Signup Page
 * 
 * User registration page with email/password signup
 * Redirects to welcome on success
 */
export default function SignupPage() {
  const router = useRouter();

  const handleSuccess = () => {
    router.push('/welcome');
  };

  return (
    <div className={styles.authPage}>
      <div className={styles.authContainer}>
        <h1 className={styles.authTitle}>Get Started</h1>
        <p className={styles.authSubtitle}>
          Create your account to start creating amazing content
        </p>
        <SignupForm onSuccess={handleSuccess} />
        <div className={styles.authFooter}>
          <p className={styles.authFooterText}>
            Already have an account?{' '}
            <a href="/login" className={styles.authLink}>
              Sign in
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
