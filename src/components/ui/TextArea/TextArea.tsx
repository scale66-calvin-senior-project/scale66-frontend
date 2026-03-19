import React from 'react';
import styles from './TextArea.module.css';

export interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

/**
 * TextArea Component
 * 
 * TODO: Implement textarea field
 * - Resizable options
 * - Character count
 * - Auto-resize functionality
 * - Error states
 */
export const TextArea: React.FC<TextAreaProps> = ({
  label,
  error,
  helperText,
  className,
  ...props
}) => {
  return (
    <div className={styles.container}>
      {label && <label className={styles.label}>{label}</label>}
      <textarea
        className={`${styles.textarea} ${error ? styles.error : ''} ${className || ''}`}
        {...props}
      />
      {error && <span className={styles.errorText}>{error}</span>}
      {helperText && !error && <span className={styles.helperText}>{helperText}</span>}
    </div>
  );
};

export default TextArea;

