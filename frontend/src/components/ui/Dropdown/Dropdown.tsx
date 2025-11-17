import React from 'react';
import styles from './Dropdown.module.css';

export interface DropdownOption {
  label: string;
  value: string | number;
}

export interface DropdownProps {
  options: DropdownOption[];
  value?: string | number;
  onChange: (value: string | number) => void;
  placeholder?: string;
  label?: string;
  className?: string;
}

/**
 * Dropdown Component
 * 
 * TODO: Implement dropdown select
 * - Custom styling
 * - Search functionality
 * - Multi-select variant
 * - Keyboard navigation
 */
export const Dropdown: React.FC<DropdownProps> = ({
  options,
  value,
  onChange,
  placeholder,
  label,
  className,
}) => {
  return (
    <div className={`${styles.container} ${className || ''}`}>
      {label && <label className={styles.label}>{label}</label>}
      <select
        className={styles.select}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default Dropdown;

