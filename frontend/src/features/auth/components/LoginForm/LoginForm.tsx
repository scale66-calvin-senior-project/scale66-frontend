import React from 'react';
import styles from './LoginForm.module.css';

export interface LoginFormProps {
  onSuccess?: () => void;
}

/**
 * LoginForm Component
 * TODO: Implement login form with email/password fields
 */
export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
  return (
    <div className={styles.container}>
      <h2>Login</h2>
      <p>TODO: Implement login form</p>
    </div>
  );
};

export default LoginForm;

