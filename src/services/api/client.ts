/**
 * API Client - Axios instance configured for backend communication
 * 
 * All requests automatically include:
 * - JWT token from Supabase auth (via interceptor)
 * - Proper error handling
 * - Type-safe responses
 * 
 * Usage:
 * ```typescript
 * import { apiClient } from '@/services/api/client'
 * 
 * // GET request
 * const { data } = await apiClient.get('/api/v1/brand-kit')
 * 
 * // POST request
 * const { data } = await apiClient.post('/api/v1/campaigns', campaignData)
 * ```
 */

import axios, { AxiosError } from 'axios'
import { env } from '@/config/env'
import { getAccessToken } from '@/lib/supabase'

// Create axios instance with base configuration
export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
})

// Request interceptor - Add JWT token to all requests
apiClient.interceptors.request.use(
  async (config) => {
    // Race getAccessToken() against a 5-second timeout so a slow/hanging
    // Supabase session check never blocks the request interceptor forever.
    const token = await Promise.race([
      getAccessToken(),
      new Promise<null>((resolve) => setTimeout(() => resolve(null), 5000)),
    ])

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors globally
apiClient.interceptors.response.use(
  (response) => {
    // Success response - return as is
    return response
  },
  async (error: AxiosError) => {
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const status = error.response.status
      
      if (status === 401) {
        // Unauthorized - redirect to login
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
      } else if (status === 403) {
        // Forbidden - user doesn't have permission
        console.error('Access forbidden:', error.response.data)
      } else if (status === 404) {
        // Not found
        console.error('Resource not found:', error.response.data)
      } else if (status >= 500) {
        // Server error
        console.error('Server error:', error.response.data)
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('No response from server:', error.message)
    } else {
      // Something else happened
      console.error('Request error:', error.message)
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
