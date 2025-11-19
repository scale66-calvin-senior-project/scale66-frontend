'use client';

import React, { createContext, useContext } from 'react';

interface AuthContextType {
  isAuthenticated: boolean;
  // TODO: Add more context properties
}

const AuthContext = createContext<AuthContextType | null>(null);

/**
 * AuthContext
 * TODO: Implement auth context
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // TODO: Implement provider
  return <AuthContext.Provider value={null}>{children}</AuthContext.Provider>;
};

export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuthContext must be used within AuthProvider');
  return context;
};
