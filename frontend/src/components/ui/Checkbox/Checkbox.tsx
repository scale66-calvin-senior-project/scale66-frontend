import React from 'react';
import styles from './Checkbox.module.css';

export interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

/**
 * Checkbox Component
 * 
 * TODO: Implement checkbox
 * - Custom checkbox styling
 * - Checked state
 * - Indeterminate state
 * - Disabled state
 */
export const Checkbox: React.FC<CheckboxProps> = ({ label, className, ...props }) => {
  return (
    <label className={`${styles.container} ${className || ''}`}>
      <input type="checkbox" className={styles.checkbox} {...props} />
      {label && <span className={styles.label}>{label}</span>}
    </label>
  );
};

export default Checkbox;

