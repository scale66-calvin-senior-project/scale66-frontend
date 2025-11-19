import React from 'react';
import styles from './SignupForm.module.css';

export interface SignupFormProps {
  onSuccess?: () => void;
}

/**
 * SignupForm Component
 * TODO: Implement signup form with email/password/name fields
 */
export const SignupForm: React.FC<SignupFormProps> = ({ onSuccess }) => {
  return (
    <div className={styles.container}>
      <h2>Sign Up</h2>
      <p>TODO: Implement signup form</p>
    </div>
  );
};

export default SignupForm;

