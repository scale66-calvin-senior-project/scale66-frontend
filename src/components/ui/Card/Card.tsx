import React from 'react';
import styles from './Card.module.css';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
}

/**
 * Card Component
 * 
 * TODO: Implement card container
 * - Base card styling with padding and border
 * - Hover effects
 * - Clickable variant
 * - Shadow states
 */
export const Card: React.FC<CardProps> = ({
  children,
  className,
  onClick,
  hoverable = false,
}) => {
  return (
    <div
      className={`${styles.card} ${hoverable ? styles.hoverable : ''} ${className || ''}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

export default Card;

