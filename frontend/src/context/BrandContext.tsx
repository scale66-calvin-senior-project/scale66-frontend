'use client';

import React, { createContext, useContext } from 'react';

interface BrandContextType {
  brandId: string | null;
  // TODO: Add more context properties
}

const BrandContext = createContext<BrandContextType | null>(null);

/**
 * BrandContext
 * TODO: Implement brand context
 */
export const BrandProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // TODO: Implement provider
  return <BrandContext.Provider value={null}>{children}</BrandContext.Provider>;
};

export const useBrandContext = () => {
  const context = useContext(BrandContext);
  if (!context) throw new Error('useBrandContext must be used within BrandProvider');
  return context;
};
