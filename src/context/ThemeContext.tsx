'use client';

import React, { createContext, useContext } from 'react';

interface ThemeContextType {
  theme: 'light' | 'dark';
  // TODO: Add more context properties
}

const ThemeContext = createContext<ThemeContextType | null>(null);

/**
 * ThemeContext
 * TODO: Implement theme context
 */
export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // TODO: Implement provider
  return <ThemeContext.Provider value={null}>{children}</ThemeContext.Provider>;
};

export const useThemeContext = () => {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useThemeContext must be used within ThemeProvider');
  return context;
};
