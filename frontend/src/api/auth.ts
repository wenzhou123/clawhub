import request from '@/utils/request'
import type { LoginCredentials, RegisterCredentials, User, ApiResponse } from '@/types'

export interface AuthResponse {
  token: string
  user: User
}

export const authApi = {
  // Login
  login(credentials: LoginCredentials): Promise<AuthResponse> {
    return request.post('/auth/login', credentials)
  },

  // Register
  register(credentials: RegisterCredentials): Promise<AuthResponse> {
    return request.post('/auth/register', credentials)
  },

  // Logout
  logout(): Promise<void> {
    return request.post('/auth/logout')
  },

  // Get current user
  getCurrentUser(): Promise<User> {
    return request.get('/auth/me')
  },

  // Refresh token
  refreshToken(): Promise<{ token: string }> {
    return request.post('/auth/refresh')
  },

  // Forgot password
  forgotPassword(email: string): Promise<void> {
    return request.post('/auth/forgot-password', { email })
  },

  // Reset password
  resetPassword(token: string, password: string): Promise<void> {
    return request.post('/auth/reset-password', { token, password })
  },

  // Verify email
  verifyEmail(token: string): Promise<void> {
    return request.post('/auth/verify-email', { token })
  }
}
