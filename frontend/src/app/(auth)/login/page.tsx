'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '@/features/auth';
import { LoginForm } from '@/features/auth';
import styles from '../auth-page.module.css';

/**
 * Login Page
 * 
 * User login page with email/password authentication
 * Redirects to dashboard on success
 */
export default function LoginPage() {
  const router = useRouter();
  const { refreshUser } = useAuth();

  const handleSuccess = async () => {
    // Refresh user data to ensure auth context is updated
    await refreshUser();
    // Small delay to ensure cookies are set
    setTimeout(() => {
      router.push('/dashboard');
    }, 100);
  };

  return (
    <div className={styles.authPage}>
      <div className={styles.authContainer}>
        <h1 className={styles.authTitle}>Welcome Back</h1>
        <p className={styles.authSubtitle}>Sign in to continue to Scale66</p>
        <LoginForm onSuccess={handleSuccess} />
        <div className={styles.authFooter}>
          <p className={styles.authFooterText}>
            Don&apos;t have an account?{' '}
            <a href="/signup" className={styles.authLink}>
              Sign up
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
