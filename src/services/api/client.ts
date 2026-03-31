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

import axios, { AxiosError, AxiosRequestConfig } from 'axios'
import { env } from '@/config/env'
import { getAccessToken, supabase } from '@/lib/supabase'

interface RetryableRequestConfig extends AxiosRequestConfig {
  _retry403?: boolean
}

// Create axios instance with base configuration
export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
})

const timeout = <T>(ms: number, fallback: T) =>
  new Promise<T>((resolve) => setTimeout(() => resolve(fallback), ms))

// Request interceptor - Add JWT token to all requests
apiClient.interceptors.request.use(
  async (config) => {
    // getAccessToken() blocks until auth is ready (up to 3s internally).
    // The outer race is a hard ceiling so a hanging Supabase call never
    // stalls the request interceptor beyond 4 seconds.
    const token = await Promise.race([getAccessToken(), timeout(4000, null)])

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
        // Could be an auth race condition on first load (INITIAL_SESSION fires
        // with null while Supabase is still refreshing the token). Retry once
        // with a fresh token before giving up.
        const config = error.config as RetryableRequestConfig
        if (config && !config._retry403) {
          config._retry403 = true
          await new Promise((r) => setTimeout(r, 300))
          const sessionResult = await Promise.race([
            supabase.auth.getSession(),
            timeout(2000, null as null),
          ])
          const session = sessionResult?.data?.session
          if (session?.access_token) {
            config.headers = { ...(config.headers ?? {}), Authorization: `Bearer ${session.access_token}` }
            return apiClient(config)
          }
        }
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
