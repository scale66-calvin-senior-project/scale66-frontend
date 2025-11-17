/**
 * API Types
 * TODO: Define API-related interfaces
 */
export interface ApiResponse<T> {
  data: T;
  error?: string;
}
