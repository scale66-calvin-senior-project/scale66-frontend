/**
 * useAuth Hook
 * 
 * Access auth state and subscription status
 */
import { useAuthContext } from '@/context/AuthContext';

export const useAuth = () => {
  return useAuthContext();
};
