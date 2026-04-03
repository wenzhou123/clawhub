import request from '@/utils/request'
import type { User, UserProfile, PaginatedResponse, Lobster } from '@/types'

export const userApi = {
  // Get user profile
  getUserProfile(username: string): Promise<UserProfile> {
    return request.get(`/users/${username}`)
  },

  // Update user profile
  updateProfile(data: {
    bio?: string
    avatar?: string
  }): Promise<User> {
    return request.put('/users/me', data)
  },

  // Change password
  changePassword(oldPassword: string, newPassword: string): Promise<void> {
    return request.put('/users/me/password', { oldPassword, newPassword })
  },

  // Get user's lobsters
  getUserLobsters(
    username: string,
    params: { page?: number; pageSize?: number } = {}
  ): Promise<PaginatedResponse<Lobster>> {
    return request.get(`/users/${username}/lobsters`, { params })
  },

  // Get current user's lobsters
  getMyLobsters(params: { page?: number; pageSize?: number } = {}): Promise<PaginatedResponse<Lobster>> {
    return request.get('/users/me/lobsters', { params })
  },

  // Upload avatar
  uploadAvatar(file: File): Promise<{ url: string }> {
    const formData = new FormData()
    formData.append('avatar', file)
    return request.post('/users/me/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // Delete account
  deleteAccount(): Promise<void> {
    return request.delete('/users/me')
  }
}
