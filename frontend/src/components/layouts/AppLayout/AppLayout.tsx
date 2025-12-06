import React from 'react';

export interface AppLayoutProps {
  children: React.ReactNode;
}

/**
 * AppLayout Component
 * 
 * Layout wrapper for authenticated app pages
 * Currently minimal - pages handle their own layouts
 */
export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return <>{children}</>;
};

export default AppLayout;
