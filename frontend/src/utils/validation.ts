/**
 * Validation Utilities
 * TODO: Implement validation functions
 */
export const isValidEmail = (email: string): boolean => {
  // TODO: Implement
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};
