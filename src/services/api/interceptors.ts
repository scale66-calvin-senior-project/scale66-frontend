/**
 * API Interceptors - Additional interceptor utilities
 * 
 * Main interceptors are configured in client.ts
 * This file provides additional helper functions for interceptor setup
 */

import { AxiosInstance, AxiosError } from 'axios'

/**
 * Setup logging interceptor for debugging
 * Logs all requests and responses in development mode
 */
export const setupLoggingInterceptor = (client: AxiosInstance) => {
  if (process.env.NODE_ENV === 'development') {
    // Request logging
    client.interceptors.request.use(
      (config) => {
        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
          data: config.data,
          params: config.params,
        })
        return config
      },
      (error) => {
        console.error('[API Request Error]', error)
        return Promise.reject(error)
      }
    )

    // Response logging
    client.interceptors.response.use(
      (response) => {
        console.log(`[API Response] ${response.status} ${response.config.url}`, {
          data: response.data,
        })
        return response
      },
      (error: AxiosError) => {
        console.error('[API Response Error]', error.response?.status, error.message)
        return Promise.reject(error)
      }
    )
  }
}

/**
 * Setup retry interceptor for failed requests
 * Retries requests that fail due to network issues
 */
export const setupRetryInterceptor = (
  client: AxiosInstance,
  maxRetries: number = 3
) => {
  client.interceptors.response.use(
    undefined,
    async (error: AxiosError) => {
      interface RetryConfig {
        __retryCount?: number;
      }
      const config = error.config as (RetryConfig & typeof error.config) | undefined

      // Don't retry if no config or max retries reached
      if (!config || (config.__retryCount !== undefined && config.__retryCount >= maxRetries)) {
        return Promise.reject(error)
      }

      // Only retry on network errors or 5xx server errors
      const shouldRetry =
        !error.response || (error.response.status >= 500 && error.response.status < 600)

      if (!shouldRetry) {
        return Promise.reject(error)
      }

      // Increment retry count
      config.__retryCount = config.__retryCount || 0
      config.__retryCount += 1

      // Exponential backoff delay
      const delay = Math.pow(2, config.__retryCount) * 1000

      console.log(`Retrying request (${config.__retryCount}/${maxRetries}) after ${delay}ms...`)

      // Wait and retry
      await new Promise((resolve) => setTimeout(resolve, delay))
      return client(config)
    }
  )
}

/**
 * Setup all interceptors
 */
export const setupInterceptors = (client: AxiosInstance) => {
  setupLoggingInterceptor(client)
  // Note: Retry interceptor disabled by default to avoid conflicts with auth
  // setupRetryInterceptor(client)
}
