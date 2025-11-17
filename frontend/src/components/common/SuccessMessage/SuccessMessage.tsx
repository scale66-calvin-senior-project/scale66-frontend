import React from 'react';
import styles from './SuccessMessage.module.css';

export interface SuccessMessageProps {
  message: string;
  onClose?: () => void;
  autoClose?: boolean;
  duration?: number;
}

/**
 * SuccessMessage Component
 * 
 * TODO: Implement success notification
 * - Success icon
 * - Auto-close functionality
 * - Toast-style positioning
 * - Smooth fade animations
 */
export const SuccessMessage: React.FC<SuccessMessageProps> = ({
  message,
  onClose,
  autoClose = true,
  duration = 3000,
}) => {
  React.useEffect(() => {
    if (autoClose && onClose) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [autoClose, onClose, duration]);

  return (
    <div className={styles.container}>
      <div className={styles.icon}>✓</div>
      <p className={styles.message}>{message}</p>
      {onClose && (
        <button onClick={onClose} className={styles.closeButton}>
          ×
        </button>
      )}
    </div>
  );
};

export default SuccessMessage;

