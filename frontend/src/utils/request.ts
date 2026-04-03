import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios'
import { ElMessage, ElLoading } from 'element-plus'
import type { ApiResponse } from '@/types'
import { useUserStore } from '@/stores/user'

// Create axios instance
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request queue for loading management
let loadingInstance: ReturnType<typeof ElLoading.service> | null = null
let requestCount = 0

const showLoading = () => {
  if (requestCount === 0) {
    loadingInstance = ElLoading.service({
      lock: true,
      text: 'Loading...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
  }
  requestCount++
}

const hideLoading = () => {
  requestCount--
  if (requestCount === 0 && loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
  }
}

// Request interceptor
request.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // Add auth token
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${userStore.token}`
    }

    // Show loading for non-silent requests
    if (!config.headers?.['X-Silent']) {
      showLoading()
    }

    return config
  },
  (error: AxiosError) => {
    hideLoading()
    return Promise.reject(error)
  }
)

// Response interceptor
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse<any>>) => {
    hideLoading()
    
    const { code, message, data } = response.data
    
    // Handle business errors
    if (code !== 200) {
      ElMessage.error(message || 'Request failed')
      return Promise.reject(new Error(message))
    }
    
    return data
  },
  (error: AxiosError) => {
    hideLoading()
    
    const { response } = error
    
    if (response) {
      const { status, data } = response as AxiosResponse
      
      switch (status) {
        case 401:
          ElMessage.error('Session expired, please login again')
          useUserStore().logout()
          window.location.href = '/login'
          break
        case 403:
          ElMessage.error('Permission denied')
          break
        case 404:
          ElMessage.error('Resource not found')
          break
        case 500:
          ElMessage.error('Server error')
          break
        default:
          ElMessage.error((data as any)?.message || 'Request failed')
      }
    } else {
      ElMessage.error('Network error')
    }
    
    return Promise.reject(error)
  }
)

export default request
